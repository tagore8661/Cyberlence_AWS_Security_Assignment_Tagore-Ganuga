from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import botocore
import json
import yaml
import time
import uuid
from utils import convert_template_to_json, convert_public_to_private

app = Flask(__name__)
CORS(app)


@app.route('/template/convert', methods=['PUT'])
def put_convert_template():
    """Convert a template JSON/YAML payload to change subnet(s) from Public to Private.
    Expects JSON body with `template` field that can be an object or string.
    Returns the modified template as JSON.
    """
    try:
        payload = request.get_json(force=True)
        if not payload or 'template' not in payload:
            return jsonify({'error': 'Request must include `template` field'}), 400

        template_in = payload['template']
        # convert to dict if it's a string
        if isinstance(template_in, str):
            template_dict = convert_template_to_json(template_in)
        else:
            template_dict = template_in

        modified = convert_public_to_private(template_dict)
        return jsonify({'modified_template': modified}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/template/<stack_name>', methods=['GET'])
def get_template(stack_name):
    """Fetch CloudFormation template for a stack and return it as JSON.
    Converts YAML to JSON if needed.
    """
    try:
        cf = boto3.client('cloudformation')
        resp = cf.get_template(StackName=stack_name)
        template_body = resp.get('TemplateBody')
        if template_body is None:
            return jsonify({'error': 'No template returned by CloudFormation'}), 404

        parsed = convert_template_to_json(template_body)
        return jsonify({'template': parsed}), 200

    except botocore.exceptions.ClientError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/changeset', methods=['POST'])
def create_changeset():
    """Create a CloudFormation ChangeSet from provided stack name and template JSON.
    Body: { 
        "stack_name": "...", 
        "template": { ... },
        "parameters": { "VpcId": "vpc-123", "InternetGatewayId": "igw-456", "PublicCidr": "10.0.1.0/24" }
    }
    Optional parameters dict for CloudFormation stack parameters.
    Polls until ChangeSet creation completes and returns status + id.
    """
    try:
        payload = request.get_json(force=True)
        stack_name = payload.get('stack_name')
        template_obj = payload.get('template')
        parameters_dict = payload.get('parameters', {})
        if not stack_name or not template_obj:
            return jsonify({'error': 'Request must include `stack_name` and `template`'}), 400

        cf = boto3.client('cloudformation')
        change_set_name = f"cs-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        template_body = json.dumps(template_obj)

        # Convert parameters dict to CloudFormation format
        # Input: { "VpcId": "vpc-123", "PublicCidr": "10.0.1.0/24" }
        # Output: [{ "ParameterKey": "VpcId", "ParameterValue": "vpc-123" }, ...]
        parameters_list = [
            {'ParameterKey': k, 'ParameterValue': str(v)}
            for k, v in parameters_dict.items()
        ] if parameters_dict else []

        try:
            kwargs = {
                'StackName': stack_name,
                'TemplateBody': template_body,
                'ChangeSetName': change_set_name,
                'ChangeSetType': 'UPDATE'
            }
            if parameters_list:
                kwargs['Parameters'] = parameters_list
            res = cf.create_change_set(**kwargs)
        except botocore.exceptions.ClientError as e:
            # If there are no changes or other known failure
            return jsonify({'error': str(e)}), 400

        # Poll for change set status
        status = None
        timeout = 60
        interval = 3
        waited = 0
        while True:
            desc = cf.describe_change_set(ChangeSetName=change_set_name, StackName=stack_name)
            status = desc.get('Status')
            if status not in ('CREATE_IN_PROGRESS', 'REVIEW_IN_PROGRESS'):
                break
            time.sleep(interval)
            waited += interval
            if waited >= timeout:
                break

        result = {
            'ChangeSetId': desc.get('ChangeSetId'),
            'Status': status,
            'StatusReason': desc.get('StatusReason')
        }
        return jsonify(result), 200

    except botocore.exceptions.ClientError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
