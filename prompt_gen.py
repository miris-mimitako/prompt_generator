import glob
import itertools

class Prompt_Generator:
  def __init__(self) -> None:
    pass

  def main(self):
    # Read text
    with open("./sorce.txt","r") as f:
      origin_text = f.readlines()

    # Define list
    swich_loc = []
    swich_text_all = []

    # Split alter text
    for text in origin_text:
      swich_text = []
      if "|" in text: 
        swich_loc.append(1)
        swich_text = text.split("|")
        swich_text_all.append(swich_text)
      else:
        swich_loc.append(0)
    
    comb_list =[]
    if not swich_text_all==[]: comb_list = self.create_list(swich_text_all)

    result_text_list = []

    if comb_list ==[]:
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
          if text[-1] == " ": text=text[:-1]
          if text[-1] == ",": text=text[:-1]
          gen_text += text + ", "
        else:
          gen_text = gen_text[:-2]
          result_text_list.append(gen_text)
    
    with open("./prompt.txt","w") as wf:
      for index, writer in enumerate(result_text_list): 
        wf.write(writer)
        if index != len(result_text_list)-1: wf.write("\n")

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
