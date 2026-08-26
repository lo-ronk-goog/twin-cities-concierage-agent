import sys
import yaml
import vertexai._genai.agent_engines
from google.agents.cli._project import read_project_config
from google.agents.cli.deploy.agent_runtime import deploy_agent_runtime

def main():
    if len(sys.argv) < 3:
        print("Usage: deploy.py <stage> <display_name>")
        sys.exit(1)
        
    stage = sys.argv[1]
    display_name = sys.argv[2]
    
    with open('agent.yaml') as f:
        manifest = yaml.safe_load(f)

    stage_key = 'dev' if stage == 'staging' else 'prod'
    env_config = manifest.get('environments', {}).get(stage_key, {})
    gateway_name = env_config.get('agent_gateway')
    service_account = env_config.get('service_account')

    if gateway_name:
        original_create_config = vertexai._genai.agent_engines.AgentEngines._create_config
        def patched_create_config(self, *args, **kwargs):
            config_val = kwargs.get('config')
            if config_val is None and len(args) > 2:
                config_val = args[2]
            
            is_identity_creation = isinstance(config_val, dict) and config_val.get('identity_type') == 'AGENT_IDENTITY'
            
            if not is_identity_creation:
                kwargs['agent_gateway_config'] = {
                    'client_to_agent_config': {
                        'agent_gateway': f'projects/lpr-gemini-enterprise-1/locations/us-central1/agentGateways/{gateway_name}'
                    }
                }
            return original_create_config(self, *args, **kwargs)
        vertexai._genai.agent_engines.AgentEngines._create_config = patched_create_config

    cfg = read_project_config()
    deploy_agent_runtime(
        cfg=cfg,
        project='lpr-gemini-enterprise-1',
        location='us-central1',
        display_name=display_name,
        service_account=service_account,
        agent_identity=True,
    )

if __name__ == '__main__':
    main()
