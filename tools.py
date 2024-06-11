from openai import OpenAI
import openai
import os

def parse_ranked_list(string_ranked_list, list_range):
    """Takes a string of a ranked list and returns a list of strings"""
    list_items = []
    lines = string_ranked_list.split('\n')
    # Loop through each line
    for line in lines:
        # Check if the line starts with a number followed by a dot (indicating an article title)
        if line.strip().startswith(tuple(f"{i}." for i in range(1, list_range))):
            # Split the line at the first dot followed by a space to isolate the title
            item = line.split('. ', 1)[1]
            # Append the isolated item (string) to the list, removing any enclosing quotes and re-adding them
            # This ensures the format is with double quotes only
            cleaned_item = item.strip()
            if cleaned_item.startswith('"') and cleaned_item.endswith('"'):
                # Remove the extra quotes and strip any excess spaces
                cleaned_item = cleaned_item[1:-1].strip()
            list_items.append(f"{cleaned_item}")
    return list_items

def get_gpt_response(prompt, gpt_model="gpt-4", json_mode=False, response_format=""):
  """Encapsulates GPT prompting
  User provides prompt and gets only the text of GPT response

  Parameters
  ----------
  prompt : str
  gpt_model : str, optional (default is "gpt-4")
    Can also input "gpt-3.5-turbo"
  response_format : str, optional
    Input "json" for json format
  Returns
  -------
  str
    text response returned by chat completion agent
  None
    if no response received by GPT
  """

  client = OpenAI(
      api_key=os.environ.get("openai_api_key"),
  )
  if response_format == "json": 
    response = client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    response_format={ "type": "json_object" },
    model=gpt_model,
    )
  else:
    response = client.chat.completions.create(
    messages=[
      {
        "role": "user",
        "content": prompt,
      }
    ],
    model=gpt_model,
    )
  if response.choices:
    response_text = response.choices[0].message.content
    return response_text
  else:
    return None

if __name__ == '__main__':
    ranked_list = """
Here is a list of the sentences and phrases from the article that best support the argument regarding the presence and discussion of a Senate AI bill:

1. "Senate Majority Leader Chuck Schumer (D-NY) today spoke on the Senate floor on the release of the Bipartisan Roadmap For Artificial Intelligence Policy."
2. "Last year, Congress faced a momentous choice: either watch from the sidelines as artificial intelligence reshaped our world, or make a novel, bipartisan effort to enhance but also regulate this technology before it was too late."
3. "I convened a bipartisan working group of Senators last year – Senators Rounds, Heinrich, and Young – to chart the path forward on AI in the Senate."
4. "After months of discussion, after hundreds of meetings, and after nine first-of-their-kind AI Insight Forums, our Bipartisan Senate Working Group released the first-ever Roadmap for AI Policy in the Senate."
5. "Our Policy Roadmap for AI is the first, most comprehensive, most bipartisan, and most forward-thinking report on AI regulation ever produced by Congress."
6. "Urgency, because AI is so complex, so rapidly evolving, and so broad in its impact – it covers almost every aspect of society."
7. "Humility – this is hard to do – because AI is nothing like Congress has ever dealt with before."
8. "Bipartisanship, because the changes that AI brings won’t discriminate between left, right, and center."
9. "Innovation must be our north star."
10. "Transformational innovation is reaching the stars."
11. "Sustainable innovation... means innovation to produce guardrails that minimize the damage that AI could bring."
12. "But our Insight Forums were designed to be balanced, with inputs of leaders from the industry."
13. "We recommend a $32 billion surge in emergency funding to secure America's dominance in AI."
14. "A bipartisan recommendation."
15. "We need our committees to continue the bipartisan momentum of the AI Gang."
16. "Achieve the hope of passing legislation by the end of the year."
17. "Our committee chairs and ranking members are ready and eager to engage in AI."
18. "Our Policy Roadmap includes many areas of bipartisan agreement that committees can use."
19. "We're making progress in the Rules Committee, which is marking up legislation today."
20. "The Commerce Committee is looking at legislation regarding AI innovation."
21. "The Homeland Security and Government Affairs Committee is considering how to leverage AI in the federal workforce."
22. "The Armed Services Committee is leading the way on AI and the military."
23. "Our Policy Roadroadmap also embraces action to protect our elections from the potential risk of AI."
24. "The 2024 elections will be the first elections ever held in the age of AI."
25. "Rules Committee, which is marking up three bills – all three with bipartisan support."
26. "Our Policy Roadmap advocates for a host of regulatory recommendations that help maximize AI’s potential and minimize its risks."
27. "These are all difficult issues to deal with, but move forward we must."
28. "Our Policy Roadmap is an important step in AI regulation."
29. "Getting the committees here in the Congress to start figuring out the bipartisan legislation that they can move forward on is a good step."
30. "I also plan to meet with Speaker Johnson in the near future to see how we can make Congress’s efforts on AI not just bipartisan, but also bicameral."
31. "It's been a long, long time, and a culmination of months of listening and thinking and working on this issue."
32. "I want to thank my colleagues in the Bipartisan Senate Working Group – Senators Rounds, Heinrich, and Young."
33. "Over 70 senators attended at least one, and many attended multiple forums."
34. "They are beginning their work on AI through the committee process."
35. "And I thank all the staff, who have put a lot effort and a lot of hours into this Policy Roadmap."
36. "I have a great staff, and they have been so instrumental in getting us to the point we're at now."
37. "Congress can't and won’t solve every challenge AI presents today, but with this Policy Roadmap, we now have a foundation necessary to propel America into the age of AI."

These sentences and phrases encapsulate key points about the Senate AI bill, the bipartisan and comprehensive approach to AI policy, and the legislative actions underway, aligning well with the argument of the presence of such a bill on the Senate floor now."""
    print(parse_ranked_list(ranked_list))