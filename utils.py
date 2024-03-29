# utils.py

import os
import csv
import math
import evaluate
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Dict, List, Optional


def load_raw_data(src_filepath: List[str], lang_code: List[str], model_name: str, 
                  trg_filepath: List[str]=None, max_length: int=256):
    len_src = len(src_filepath)
    text_data = {'src_text': []}
    token_data = []
    if len_src != len(lang_code):
        raise Exception("Lengths of src_filepath and lang_code don't match.")
    
    if trg_filepath:
        text_data['target_text'] = []
        if len_src != len(trg_filepath):
            raise Exception("Lengths of src_filepath and trg_filepath don't match.")
        is_trg = True
    lang_code = [
            'cni_Latn', 
            'aym_Latn', 
            'bzd_Latn', 
            'gn_Latn', 
            'oto_Latn', 
            'nah_Latn', 
            'quy_Latn', 
            'tar_Latn', 
            'shp_Latn', 
            'hch_Latn'
            ]
    lang_code_to_add = [
            'cni_Latn', 
          #  'aym_Latn', 
            'bzd_Latn', 
           # 'gn_Latn', 
            'oto_Latn', 
            'nah_Latn', 
           # 'quy_Latn', 
            'tar_Latn', 
            'shp_Latn', 
            'hch_Latn'
            ]
    for i in range(len_src):
        src_path = src_filepath[i]
        code = lang_code[i]
        tokenizer = AutoTokenizer.from_pretrained(model_name, src_lang="spa_Latn", tgt_lang=code, additional_special_tokens = lang_code_to_add)
        print('oto_Latn' in tokenizer.additional_special_tokens)
        tokenizer.tgt_lang = code
        with open(src_path) as f:
            for line in f:
                text_data['src_text'].append(line.strip())

        if is_trg:
            trg_path = trg_filepath[i] 
            with open(trg_path) as f:
                for line in f:
                    text_data['target_text'].append(line.strip())

            for src_text, trg_text in zip(text_data['src_text'], text_data['target_text']):
                token_data.append(tokenizer(src_text, text_target=trg_text, 
                                            max_length=max_length, padding='max_length', truncation=True))
        else:
            for src_text in text_data['src_text']:
                token_data.append(tokenizer(src_text, max_length=max_length, padding='max_length', truncation=True))

    return token_data




def predict(
    model: nn.Module, 
    dataloader: DataLoader, 
    tokenizer: AutoTokenizer, 
    device: torch.device
) -> List[List[int]]:
    model.eval()
    preds = []
    
    with torch.no_grad():
        for batch in tqdm(dataloader):
            inputs = batch.to(device)

            logits = model.generate(**inputs, max_length=256,
                                    forced_bos_token_id=tokenizer.lang_code_to_id["spa_Latn"])
            
            preds.append(logits)
                    
    return preds