from utils.agent import _run   
    
def run(environment, content):
    actions = '"Label"'
    Environment_parameters = environment
    supplementary_rules = ""
    question = [{"role": "system", "content": 
                    f"""
                    You are operateGPT, a professional assistant who operates annotating software for me. I will input a complex goal, please decompose the complex goal into several structured simple goals by your professional knowledge and system status.

                    Generate output according to the following main rules:
                    1. Input is a complex target. Convert it into a series of simple sub goals.
                    2. Each sub goal should be composed of five tuples: "Action", "Object", "Start Page", "End Page", and "Information".
                    3. "Action" is the action required for this operation, which can only be one of {actions}
                    4. "Object" refers to the target of an action, which is a description of a type of object.
                    5. "Start page" is a number used to specify the page where the operation starts.
                    6. "end" is a number used to specify the page where the operation ends.
                    7. "info" is the Supplementary Information for "Action".
                    Please also refer to the following supplementary rules: {supplementary_rules}
                    The output uses the following format:
                    1. ("Operation", "Object", "Start Page", "End Page", "Information")

                    System Status is here:{Environment_parameters}
                    """
                    },
                    {"role": "user", "content": 
                    f"""
                    {content}
                    """
                }]

    return _run(question)
