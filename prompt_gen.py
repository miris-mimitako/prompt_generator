from pathlib import Path
from glob import glob
import itertools
import json
from datetime import datetime
import os
from pathlib import Path
from chardet import detect

class Prompt_Generator:
  def __init__(self) -> None:
    with open("./config.json","rb") as bf:
      bf_read = bf.read()
      dict_config_encoding = detect(bf_read)
      try:
        with open("./config.json",encoding=dict_config_encoding["encoding"]) as json_config:
          self.dic_config = json.load(json_config)
      except:
        raise ("config.jsonのエンコーディングが不明です。")

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
      if text.rfind("|") == len(text)-1: text = text[:-1]
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

    if config_["output_settings"]["main_name"]:
      file_name = config_["output_settings"]["main_name"]
    else:
      file_name = "prompt"

    # prefix settings
    if config_["output_settings"]["file_prefix"]:
      prefix = self.pre_suf_fix_file_name_settings(config_["output_settings"]["file_prefix"], output_path)
      file_name = prefix + "-" + file_name

    # suffix settings
    if config_["output_settings"]["file_suffix"]:
      suffix = self.pre_suf_fix_file_name_settings(config_["output_settings"]["file_suffix"], output_path)
      file_name = file_name + "-" + suffix

    # to convert text file
    file_name += ".txt" 

    with open(os.path.join(output_path,file_name),"w") as wf:
      for index, writer in enumerate(result_text_list): 
        wf.write(writer)
        if index != len(result_text_list)-1: wf.write("\n")

    print("end app")

  def pre_suf_fix_file_name_settings(self,setting_text, output_path):
    if "{date}" in setting_text:
      now = datetime.now()
      str_datetime_now = now.strftime("%Y%m%d-%H%M%S")
      prefix = setting_text.replace("{date}", str_datetime_now)
    if "{order_num}" in setting_text:
      prefix = prefix.replace("{order_num}", str(len(list(Path(output_path).glob("*.txt"))) + 1))

      return prefix

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
      dot_count = out_path_text.count(".")
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
        raise ("Directory generation error: Cannot create a folder more than 2 upper levels. ")
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
