import os
from typing import List
import torch
from summarizer import TransformerSummarizer
from transformers import pipeline
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

from generator import config as C
from generator.constants import SummaryModel


class SummaryService:
    __BASE_MODEL_DIR = os.getenv('BASE_DIR') + 'generator/models/summary/'

    @classmethod
    def generate_summary(cls, phrase: str, corpus: List[str], summary_model: SummaryModel) -> str:
        summary = cls.run_gtp2(cls, phrase, corpus)
        summary = cls.clear_summary(cls, phrase, summary)

        return summary

    def clear_summary(self, phrase: str, summary: str) -> str:
        summary = summary.strip()
        summary = summary.replace('  ', ' ')

        if summary.lower().startswith(phrase.lower()):
            summary = summary[len(phrase):]

        return summary

    def run_xlnet(self, phrase: str, corpus: List[str]) -> str:
        body = ''.join(corpus)
        body = phrase + ' ' + body

        model = TransformerSummarizer(transformer_type="XLNet",transformer_model_key="xlnet-base-cased")
        summary = ''.join(model(body, min_length=C.MIN_SUMMARY_LENGTH, max_length=C.MAX_SUMMARY_LENGTH))

        return summary

    def run_gtp2(self, phrase: str, corpus: List[str]) -> str:
        body = ''.join(corpus)
        body = phrase + ' ' + body

        model = TransformerSummarizer(transformer_type='GPT2', transformer_model_key='distilgpt2')
        summary = ''.join(model(body, min_length=C.MIN_SUMMARY_LENGTH, max_length=C.MAX_SUMMARY_LENGTH))

        return summary

    def run_distill_bart_cnn(self, corpus: List[str]) -> str:
        summarization_pipeline = pipeline('summarization', self.__BASE_MODEL_DIR + 'distill-bart-cnn')
        
        min_sequence_length = 1 * 512
        max_sequence_length = 3 * 512

        corpus_parts = ['']
        part_counter = 0
        for part in corpus:
            if len(corpus_parts[part_counter]) < max_sequence_length:
                corpus_parts[part_counter] += part
            else:
                part_counter += 1
                corpus_parts.append(part)

        summary = ''
        for part in corpus_parts:
            if len(part) > min_sequence_length:
                try:
                    summary += ' ' + summarization_pipeline(part)[0]['summary_text']
                except:
                    pass

        return summary

    def run_distill_pegasus_cnn(self, corpus: List[str]) -> str:
        torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
        tokenizer = PegasusTokenizer.from_pretrained(self.__BASE_MODEL_DIR + 'distill-pegasus-cnn-16-4')
        model = PegasusForConditionalGeneration.from_pretrained(self.__BASE_MODEL_DIR + 'distill-pegasus-cnn-16-4').to(torch_device)

        min_sequence_length = 1 * 2048
        max_sequence_length = 2 * 2048

        corpus_parts = ['']
        part_counter = 0
        for part in corpus:
            if len(corpus_parts[part_counter]) < max_sequence_length:
                corpus_parts[part_counter] += part
            else:
                part_counter += 1
                corpus_parts.append(part)

        summary = ''
        for part in corpus_parts:
            if len(part) > min_sequence_length:
                try:
                    text_data = [part]
                    batch = tokenizer.prepare_seq2seq_batch(text_data, truncation=True, padding='longest', return_tensors='pt').to(torch_device)
                    summary_encoded = model.generate(**batch)
                    summary += ' ' + tokenizer.batch_decode(summary_encoded, skip_special_tokens=True)[0]
                except:
                    pass

        return summary
