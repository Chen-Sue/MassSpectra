import torch
import os 
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu' ) # "cuda:4" or ['/gpu:4', '/gpu:5']
from d2l import torch as d2l

from utils_function import load_data_nmt, bleu
from prepare_mass_spectra import input_mass_spectra
from prepare_smiles import output_smiles
from seq_to_seq import Seq2SeqEncoder, Seq2SeqDecoder, train_seq2seq, predict_seq2seq
import config 

batch_size = config.batch_size
split_ratio = config.split_ratio
src_num_steps = config.src_num_steps
tgt_num_steps = config.tgt_num_steps
embed_size = config.embed_size
num_hiddens = config.num_hiddens
num_layers = config.num_layers
dropout = config.dropout
lr = config.lr
num_epochs = config.num_epochs
split_ratio = config.split_ratio

tensor_mass_spectra, length_new_mass_spectras, new_mass_spectras = input_mass_spectra()
tensor_smiles, smiles = output_smiles()

test_iter, src_vocab, tgt_vocab = load_data_nmt(
    batch_size=batch_size, source=new_mass_spectras[split_ratio:], target=smiles[split_ratio:], 
    src_num_steps=src_num_steps, tgt_num_steps=tgt_num_steps)

encoder = Seq2SeqEncoder(len(src_vocab), embed_size, num_hiddens, num_layers, dropout)
decoder = Seq2SeqDecoder(len(tgt_vocab), embed_size, num_hiddens, num_layers, dropout)
net = d2l.EncoderDecoder(encoder, decoder)

train_seq2seq(net, test_iter, lr, num_epochs, tgt_vocab,  device)

# 应该是保存model，再调用保存好的model

src_test = new_mass_spectras[int(len(tensor_mass_spectra)*split_ratio):]
tgt_test = smiles[int(len(tensor_smiles)*split_ratio):]

for src, tgt in zip(src_test, tgt_test):
    translation, attention_weight_seq = predict_seq2seq(net, src, src_vocab, tgt_vocab, src_num_steps, tgt_num_steps, device)
    print(f'{src} => {translation}, bleu {bleu(translation, tgt, k=2):.3f}')
