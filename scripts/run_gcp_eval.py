import subprocess
import json
import ssl
import urllib.request
from datetime import datetime, timezone

def run_evaluation():
    ctx = ssl._create_unverified_context()
    token = subprocess.check_output(['gcloud', 'auth', 'print-access-token']).decode().strip()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-4] + 'Z'
    display_name = f'Evaluation Run {now_str}'

    instruction = (
        "You are a friendly, expert local concierge for the Minneapolis-Twin Cities area. "
        "Your goal is to help users plan the perfect day or night out, specifically focusing on "
        "coffee shops, casual bars, and live jazz venues. You must always verify venue operating hours, "
        "locations, and live music schedules before making a recommendation. Do not guess or hallucinate venue information. "
        "Always format your final recommendations beautifully as structured lists with emojis for clarity.\n\n"
        "You have access to a Google Cloud BigQuery database via an MCP tool. The database is located in the project `lpr-gemini-enterprise-1` under the dataset `msp_coffee_and_music`. It contains three tables you must use to verify your recommendations:\n"
        "1. `venues`: Contains `venue_id`, `name`, `city`, `neighborhood`, `category`, and `vibe`.\n"
        "2. `operating_hours`: Contains `venue_id`, `day_of_week`, `open_time`, and `close_time`.\n"
        "3. `events`: Contains `event_id`, `venue_id`, `event_date`, `artist`, `genre`, and `start_time`.\n\n"
        "When a user asks for a recommendation, write a SELECT query joining these tables as needed to ensure the venue matches their vibe, is open during their requested timeframe, and has the appropriate live music scheduled. You must execute this query using the tool `execute_sql_readonly` by passing the SQL query string in the `query` argument. CRITICAL: Do not write python code blocks, do not use the python code interpreter, and do not wrap the tool call in python statements or print functions. Always invoke the tool `execute_sql_readonly` directly as a standard model tool call."
    )

    body = {
      'displayName': display_name,
      'dataSource': {
        'evaluationSet': 'projects/152008061700/locations/us-central1/evaluationSets/4573038184711061504'
      },
      'evaluationConfig': {
        'metrics': [
          {
            'metric': 'multi_turn_trajectory_quality_v1',
            'metricConfig': {
              'predefinedMetricSpec': {
                'metricSpecName': 'multi_turn_trajectory_quality_v1',
                'metricSpecParameters': {}
              }
            }
          }
        ],
        'outputConfig': {
          'gcsDestination': {
            'outputUriPrefix': 'gs://lpr-gemini-enterprise-1-tc-concierage-agent-logs'
          }
        }
      },
      'inferenceConfigs': {
        'twin_cities_concierge': {
          'agentRunConfig': {
            'agentEngine': 'projects/lpr-gemini-enterprise-1/locations/us-central1/reasoningEngines/6500604663748886528',
            'userSimulatorConfig': {
              'maxTurn': 5
            }
          },
          'agents': {
            'twin_cities_concierge': {
              'agentId': 'twin_cities_concierge',
              'agentType': 'LlmAgent',
              'description': 'Twin Cities local concierge agent that recommends coffee shops, bars, and live music events by querying BigQuery.',
              'instruction': instruction,
              'tools': [
                {
                  'functionDeclarations': [
                    {
                      'name': 'execute_sql_readonly',
                      'description': 'Executes a read-only SQL query against the msp_coffee_and_music database project lpr-gemini-enterprise-1 containing tables venues, operating_hours, and events. Returns tabular database results.',
                      'parameters': {
                        'type': 'OBJECT',
                        'properties': {
                          'query': {
                            'type': 'STRING',
                            'description': 'The complete, read-only SQL SELECT query string to execute.'
                          }
                        },
                        'required': [
                          'query'
                        ]
                      }
                    }
                  ]
                }
              ]
            }
          }
        }
      }
    }

    url = 'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/152008061700/locations/us-central1/evaluationRuns'
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')

    with urllib.request.urlopen(req, context=ctx) as resp:
        res = json.loads(resp.read().decode())
        print('Evaluation Run Successfully Created:')
        print(json.dumps(res, indent=2))
        return res

if __name__ == '__main__':
    run_evaluation()
