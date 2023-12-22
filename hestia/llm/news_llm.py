from llama_cpp import Llama


llm = Llama(model_path="C:/Users/avity/Projects/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_threads=4,
            n_threads_batch=4,
            n_ctx=2048)



# now to turn this into a function
def chat_completion(sytem_prompt: str, user_prompt: str):
    output = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": f"{sytem_prompt}"
            },
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ], max_tokens=1024
        
    )
    return output

        
if __name__ == "__main__":
    system_prompt = """You are a news reporter. You are writing a brief summary of the news for the day."""
    user_prompt = """News:
    Scientists spot recent volcanic activity on Earths neighbour Mars - WION.
China's Space Plane Deployed 6 "Mysterious Wingmen" In Orbit, Claims Amateur Astronomer - NDTV.
Bad Weather Delays Intuitive Machines Lunar Lander Mission - Aviation Week.
NASA's moon landing mission will include a non-American, Harris will announce - POLITICO.
How to Spot Your Favorite Constellations | Star Gazers - South Florida PBS.
Meet 'Coscientist,' your AI lab partner: System succeeds in planning and carrying out real-world chemistry experiments - Phys.org.
From dog to tortoise, 5 strange animals that were sent to space - IndiaTimes.
Spectacular Celestial Geminid Meteor Shower 2023 Captured by Hanle - Kashmir Life.
Adorable Cat Video Reaches Earth After 19-Million-Mile Journey from Deep Space - Gizmodo.
Microplastics Are the Not-So-Secret Ingredient in Marine Snow - Eos.
NASAs Mars Reconnaissance Orbiter Has Captured Images of Something Odd Carved into the Martian Landscape - The Debrief.
SETI has discovered a new 'slide whistle' like fast radio burst signal - Interesting Engineering.
NASA discovers "Christmas Tree Cluster" of stars glowing in space: "It's beginning to look a lot like cosmos" - CBS News.
Chinese Spaceplane Trailed By Six Mysterious Objects Transmitting Repeating Pattern - IFLScience.
ESA - Pinhole propulsion for satellites - European Space Agency.
"""
    output = chat_completion(system_prompt, user_prompt)
    print(output)
    
    