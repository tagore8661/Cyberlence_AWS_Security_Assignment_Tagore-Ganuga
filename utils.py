import json
import yaml


def convert_template_to_json(template_body):
    """Accepts a template body (YAML or JSON string or dict) and returns a Python dict."""
    if isinstance(template_body, dict):
        return template_body

    if isinstance(template_body, str):
        s = template_body.strip()
        # try JSON first
        try:
            return json.loads(s)
        except Exception:
            pass

        # try YAML — handle CloudFormation short tags (e.g. !Ref, !If, !Not)
        try:
            # Add a multi-constructor to map CFN short tags to JSON-style keys
            def cfn_multi_constructor(loader, tag_suffix, node):
                # Map short tag name to CloudFormation JSON function name
                tag_map = {
                    'Ref': 'Ref',
                    'GetAtt': 'Fn::GetAtt',
                    'Sub': 'Fn::Sub',
                    'Base64': 'Fn::Base64',
                    'If': 'Fn::If',
                    'Not': 'Fn::Not',
                    'Equals': 'Fn::Equals',
                    'And': 'Fn::And',
                    'Or': 'Fn::Or',
                    'Join': 'Fn::Join',
                    'Select': 'Fn::Select',
                    'FindInMap': 'Fn::FindInMap',
                    'ImportValue': 'Fn::ImportValue',
                    'Cidr': 'Fn::Cidr',
                }

                key = tag_map.get(tag_suffix, tag_suffix)
                if isinstance(node, yaml.ScalarNode):
                    value = loader.construct_scalar(node)
                elif isinstance(node, yaml.SequenceNode):
                    value = loader.construct_sequence(node)
                elif isinstance(node, yaml.MappingNode):
                    value = loader.construct_mapping(node)
                else:
                    value = loader.construct_scalar(node)

                return {key: value}

            Loader = yaml.SafeLoader
            # register multi constructor only once
            if not hasattr(Loader, '_cfn_multi_ctor_added'):
                Loader.add_multi_constructor('!', cfn_multi_constructor)
                setattr(Loader, '_cfn_multi_ctor_added', True)

            obj = yaml.load(s, Loader=Loader)
            return obj
        except Exception as e:
            raise ValueError(f"Template body is not valid JSON or YAML: {e}")

    raise ValueError('Unsupported template body type')


def convert_public_to_private(template_dict):
    """Modify a CloudFormation template dict to convert public subnet behavior to private.

    Strategy (simple and safe for assignment purposes):
    - Remove `AWS::EC2::Route` resources that route 0.0.0.0/0 (or ::/0) to an Internet Gateway
    - For `AWS::EC2::Subnet` resources, set `MapPublicIpOnLaunch` to False if present
    - Return the modified template dict (a deep-modify of the provided dict)
    """
    if not isinstance(template_dict, dict):
        raise ValueError('Template must be a dict')

    resources = template_dict.get('Resources') or {}
    to_delete = []

    for name, res in list(resources.items()):
        rtype = res.get('Type')
        props = res.get('Properties') or {}

        if name == 'CFNRouteTableAssoc':
            to_delete.append(name)

        # Remove route entries that point default route to a GatewayId (IGW)
        if rtype == 'AWS::EC2::Route':
            dest = props.get('DestinationCidrBlock') or props.get('DestinationIpv6CidrBlock')
            gw = props.get('GatewayId')
            if dest in ('0.0.0.0/0', '::/0') and gw:
                #to_delete.append(name)
                props['GatewayId'] = {'Ref': 'AWS::NoValue'}

        

        # For subnets, ensure MapPublicIpOnLaunch is false
        if rtype == 'AWS::EC2::Subnet':
            if 'MapPublicIpOnLaunch' in props and props.get('MapPublicIpOnLaunch') is True:
                props['MapPublicIpOnLaunch'] = False

    for name in to_delete:
        resources.pop(name, None)

    template_dict['Resources'] = resources
    return template_dict
