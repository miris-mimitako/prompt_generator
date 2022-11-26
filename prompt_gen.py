import glob
import itertools
import json
from datetime import datetime
import os
from pathlib import Path

class Prompt_Generator:
  def __init__(self) -> None:
    try:
      try:
        with open("./config.json",encoding="utf-8") as jf:
          self.dic_config = json.load(jf)
      except:
        with open("./config.json",encoding="cp932") as jf:
          self.dic_config = json.load(jf)
    except:
      raise ("config.json shall set encoding utf-8 or cp932")

  def main(self):
    print("start app")
    config_ = self.dic_config.copy()

    # Read text
    if config_["dir"]["input_text"]:
      parent_path = Path(__file__).parent
      file_path = os.path.join(parent_path,config_["dir"]["input_text"])
      with open(file_path,"r") as f:
        origin_text = f.readlines()
    else:
      with open("./source.txt","r") as f:
        origin_text = f.readlines()

    # Define list
    swich_loc = []
    swich_text_all = []

    # Split alter text
    for text in origin_text:
      swich_text = []
      if "\n" in text: text=text[:-1] 
      if text.find("|") == 0: text = text[1:]
      if text.rfind("|") == len(text)-1: text = text[:-1]
      if text.rfind("|") == len(text)-1 :text = text[:-1]
      if "|" in text:
        swich_loc.append(1)
        swich_text = text.split("|")
        swich_text_all.append(swich_text)
      else:
        swich_loc.append(0)
    
    comb_list =[]
    if not swich_text_all==[]: comb_list = self.create_list(swich_text_all)

    result_text_list = []
    
    # create prompt
    if comb_list ==[]:
      # Not use split text
      gen_text = ""
      for text in origin_text:
        if "\n" in text: text=text[:-1] 
        if "*" in text: text = self.strong_prompt(text=text)
        if "/" in text: text = self.weak_prompt(text=text)
        gen_text += text + ", "
      else:
        gen_text = gen_text[:-2]
        result_text_list.append(gen_text)
    else:
      # use split text
      for c_list in comb_list:
        counter = 0
        gen_text = ""
        for text,loc_ in zip(origin_text, swich_loc):
          if loc_: 
            text=c_list[counter]
            counter +=1
          if "\n" in text: text=text[:-1] 
          if "*" in text: text = self.strong_prompt(text=text)
          if "/" in text: text = self.weak_prompt(text=text)
          if text.rfind(" ") == len(text): text=text[:-1]
          if text.rfind(",") == len(text): text=text[:-1]
          gen_text += text + ", "
        else:
          gen_text = gen_text[:-2]
          result_text_list.append(gen_text)

    # make dir
    if config_["dir"]["output_path"]:
      output_path = self.output_path_gen(config_["dir"]["output_path"])
    else:
      output_path = Path(__file__).parent

    # write prompt
    file_name = config_["output_settings"]["main_name"]
    if config_["output_settings"]["file_prefix"] == "date":
      now = datetime.now()
      prefix = now.strftime("%Y%m%d-%H%M%S-")
      file_name = prefix + file_name

    if config_["output_settings"]["file_sufix"]:
      file_name = file_name + "-" + str(config_["output_settings"]["file_sufix"])

    file_name += ".txt"

    print(output_path)

    with open(os.path.join(output_path,file_name),"w") as wf:
      for index, writer in enumerate(result_text_list): 
        wf.write(writer)
        if index != len(result_text_list)-1: wf.write("\n")

    print("end app")

  def output_path_gen(self,out_path_text):
    """
    To mak output path
    """
    if out_path_text.find(":")>0:
      #Absorute path
      print(out_path_text.find(":"))
      os.makedirs(out_path_text,exist_ok=True)
      file_path = out_path_text
    else:
      dot_count = out_path_text.count() ## error
      if not dot_count:
        parent_path = Path(__file__).parent
        file_path = os.path.join(parent_path,out_path_text)
      elif dot_count == 1:
        parent_path = Path(__file__).parent
        prep_path = out_path_text[1:]
        if prep_path[0] == "/":prep_path=prep_path[1:]
        file_path = os.path.join(parent_path,prep_path)
      elif dot_count == 2:
        parent_path = Path(__file__).parent.parent
        prep_path = out_path_text[2:]
        if prep_path[0] == "/":prep_path=prep_path[1:]
        file_path = os.path.join(parent_path,prep_path)
      else:
        raise ("Directory generation error: Cannot create a folder more than 3 upper levels. ")
      os.makedirs(file_path,exist_ok=True)
      return file_path

  """
  Prompt creation
  """

  def create_list(self,l_text):
    result_list = list(itertools.product(*l_text))
    print(result_list)
    return result_list

  def strong_prompt(self,text):
    count_ = text.count("*")
    text = text.replace("*","")
    if text[-1] == " ": text=text[:-1]
    if text[-1] == ",": text=text[:-1]
    new_text = "("*count_ + text + ")"*count_
    return new_text

  def weak_prompt(self,text):
    count_ = text.count("/")
    text = text.replace("/","")
    if text[-1] == " ": text=text[:-1]
    if text[-1] == ",": text=text[:-1]
    new_text = "["*count_ + text + "]"*count_
    return new_text

  def __del__(self):
    pass

if __name__=="__main__":
  PG = Prompt_Generator()
  PG.main()
