import yaml
from pathlib import Path

class PromptManager():
    def __init__(self):
        """
        Initialize the PromptManager.

        The PromptManager reads all YAML files in the same directory as this file
        and loads them into a dictionary where the keys are the filenames (without extension)
        and the values are the contents of the YAML files.
        """
        self.prompts = {}
        
        # prompt manager is in models/prompt_manager.py, prompts are in prompt/*..
        root_path = Path(__file__).parent.parent
        prompt_folder = root_path / "prompt"      
        
        for prompt_file in prompt_folder.glob("*.yaml"):
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.prompts[prompt_file.stem] = yaml.safe_load(f)

    def get_prompt(self, file_key, prompt_key, **kwargs):
        """
        Get a prompt template from a YAML file and format it with kwargs.

        Args:
            file_key (str): The key of the YAML file to retrieve the prompt from.
            prompt_key (str): The key of the prompt to retrieve from the YAML file.
            **kwargs: Keyword arguments to format the prompt template with.

        Returns:
            str: The formatted prompt template.

        Raises:
            KeyError: If the prompt_key is not found in the YAML file specified by file_key.
        """
        try:    
            if file_key not in self.prompts:
                raise KeyError(f"File '{file_key}.yaml' not loaded.")
            
            # 2. Get the specific template (system_prompt or user_prompt)
            template = self.prompts[file_key].get(prompt_key)
            
            if not template:
                raise KeyError(f"Key '{prompt_key}' missing in {file_key}.yaml")
            
            # .format(**kwargs) associa automaticamente {user_input} al valore user_input="..."
            return template.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Key '{prompt_key}' not found in '{file_key}.yaml. Details: {e}'")
        
if __name__ == "__main__":
    pm = PromptManager()
    args = {
        "system": {},
        "user": {
            "user_input": "",
            "history": "",
            "context ": "",
            "query": ""
        }
    }
    prompt = pm.get_prompt("data_analyst", "user_prompt")
    print(prompt)
