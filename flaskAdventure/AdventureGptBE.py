# AdventureGPTBE Class - a back end class to drive an adventure game
# using the chat completion capability of OpenAI's ChatGPT

import os
import time
#from dotenv import load_dotenv
import openai

from flask import g


def get_gpt():
  if 'gpt' not in g:
    g.gpt = AdventureGptBE()
  return g.gpt


class AdventureGptBE:
  """A Class to manage ChatGPT interactions for an adventure game.

    To use this class, instantiate:
    gptBE = AdventureGptBE()
        this runs init_game() which loads the OPENAI_API_KEY that is required to interact with OpenAI's chatbot

    then you can run
    textDescription = gptBE.gameIntro()
    to get a text description of the game. We can use this on the front page of a web app.

    Then do iterations of calling:
        result, choices = adventure.generate_a_result(a_choice, result)

    """

  def __init__(self):
    self.api_token = None
    self.game_structure = self.define_game_structure()
    self.base_prompt = ""
    self.init_game()

  def load_api_key(self):
    #load_dotenv()
    #self.api_token = os.getenv("OPENAI_API_KEY")
    self.api_token = os.environ['OPENAI_API_KEY']
    openai.api_key = self.api_token

  def define_game_structure(self):
    game_structure = """
        You are an AI helping the player play an endless turn based text adventure game. 
        You will stay in character as the Game Master. As Game Master, never let the player die.
        They always survive a situation, no matter how harrowing. On each turn provide a 
        description of the surroundings, list any items the player is carrying, and then offer 
        four numbered actions for what the player can do next. Keep the actions short with no 
        more than four words in each option."""
    return game_structure

  def build_base_prompt(self, goal, location):
    base_prompt = """The goal of the game is for the player to {0}. 
        The setting of the game is {1}.""".format(goal, location)
    return base_prompt

  def init_game(self):
    self.load_api_key()
    if self.api_token is None:
      raise 'An OpenAI API Key has to be specified to play this game. Missing API Key'
    goal = "fix their spaceship and escape from the alien planet"
    start_location = "on an alien planet with man eating dinosaur like monsters"
    self.base_prompt = self.build_base_prompt(goal, start_location)

  def game_intro(self):
    # Send base prompt to ChaptGPT and then enter a loop
    # print('Consulting the Oracle ...')
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {
          "role": "system",
          "content": self.game_structure
        },
        {
          "role": "system",
          "content": self.base_prompt
        },
        {
          "role": "user",
          "content": "Describe the premise of the game."
        },
      ])
    result = response.choices[0].message.content
    return result

  def generate_the_next_game_step(self, choice, last_result):
    waitingForNextGameStep = True
    while waitingForNextGameStep:
      try:
        last_result = self.get_next_turn_from_chatbot(choice, last_result)
        waitingForNextGameStep = False
      except openai.error.RateLimitError:
        self.pause_game()
    return last_result

  def generate_possible_actions(self, last_result):
    waitingForNextGameStep = True
    while waitingForNextGameStep:
      print('The universe continues to spin ...')
      try:
        choices = self.get_choices_from_chatbot(last_result)
        last_result = "{0} {1}".format(last_result, choices)
        waitingForNextGameStep = False
      except openai.error.RateLimitError:
        self.pause_game()
    return last_result

  def strip_choices_from_result(self, result):
    offset = 0
    firstOne = result.find('1. ')
    if result[firstOne + 2:].find('1. ') != -1:
      offset = firstOne
    just_result = result[0:offset + result.find('1. ')]
    choices = []
    choices.append(result[offset + result[offset:].find('1. '):offset +
                          result[offset:].find('2. ')].strip())
    choices.append(result[offset + result[offset:].find('2. '):offset +
                          result[offset:].find('3. ')].strip())
    choices.append(result[offset + result[offset:].find('3. '):offset +
                          result[offset:].find('4. ')].strip())
    choices.append(result[offset + result[offset:].find('4. '):].strip())
    return just_result, choices

  def generate_a_result(self, choice, last_result):
    tmp_result = self.generate_the_next_game_step(choice, last_result)
    if self.result_has_no_choices(tmp_result):
      tmp_result = self.generate_possible_actions(tmp_result)
    new_result, choices = self.strip_choices_from_result(tmp_result)
    return new_result, choices

  def get_choices_from_chatbot(self, last_result):
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{
        "role": "system",
        "content": self.game_structure
      }, {
        "role": "system",
        "content": self.base_prompt
      }, {
        "role": "assistant",
        "content": last_result
      }, {
        "role": "user",
        "content": "Give me a set of 4 options what I can do next"
      }])
    last_result = response.choices[0].message.content
    return last_result

  def get_next_turn_from_chatbot(self, choice, last_result):
    the_message = self.build_message(choice, last_result)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                            messages=the_message)
    last_result = response.choices[0].message.content
    return last_result

  def pause_game(self):
    print('Hit OpenAI rate limit. Stretch your legs for a bit!')
    print('Sleeping for 30 seconds ...')
    time.sleep(10)
    print('  20 seconds')
    time.sleep(10)
    print('  10 seconds')

  def result_has_no_choices(self, result):
    has_no_choices = True
    if (result.find('1. ') != -1) and (result.find('2. ') != -2) and \
        (result.find('3. ') != -1):
      has_no_choices = False
    return has_no_choices

  def build_message(self, choice, last_result):
    message = [{
      "role": "system",
      "content": self.game_structure
    }, {
      "role": "system",
      "content": self.base_prompt
    }]
    if len(last_result) > 0:
      message.append({"role": "assistant", "content": last_result})
    if len(choice) == 0:
      message.append({"role": "user", "content": "Describe what I see."})
    else:
      message.append({
        "role":
        "user",
        "content":
        "Describe what happens when I {0}.".format(choice)
      })
    return message


if __name__ == '__main__':
  adventure = AdventureGptBE()
  description = adventure.game_intro()
  print('## Game Description ##')
  print(description)
  print('## First Game Step ##')
  result, choices = adventure.generate_a_result("", "")
  print(result)
  for choice in choices:
    print(choice)
  result, choices = adventure.generate_a_result(choices[0], result)
  print('## Second Game Step ##')
  print(result)
  for choice in choices:
    print(choice)
  result, choices = adventure.generate_a_result(choices[2], result)
  print('## Third Game Step ##')
  print(result)
  for choice in choices:
    print(choice)
