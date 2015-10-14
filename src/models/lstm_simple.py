# Author: Michal Lukac, cospelthetraceur@gmail.com
# script for training RNN for rossmann
# You need to have pandas, numpy, scipy and keras

from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.optimizers import SGD, Adagrad, Adadelta, RMSprop, Adam

from pandas import HDFStore
import cPickle
import pandas as pd
import numpy as np
import random
from random import shuffle
import os.path

from helper import *

# which columns we will use for model
columns = ['Store', 'CompetitionDistance', 'Promo2', 'Open', 'Promo',
           'StateHoliday_a','StateHoliday_b', 'StateHoliday_c','StateHoliday_0',
           'Assortment_a','Assortment_b','Assortment_c','Assortment_nan',
           'StoreType_a','StoreType_b','StoreType_c','StoreType_d','StoreType_nan',
           'DayOfWeek_1.0','DayOfWeek_2.0','DayOfWeek_3.0','DayOfWeek_4.0','DayOfWeek_5.0','DayOfWeek_6.0','DayOfWeek_7.0',
           'WeekOfMonth_1.0','WeekOfMonth_2.0','WeekOfMonth_3.0','WeekOfMonth_4.0','WeekOfMonth_5.0','WeekOfMonth_6.0',
           'Month_1.0','Month_2.0','Month_3.0','Month_4.0','Month_5.0','Month_6.0','Month_7.0','Month_8.0','Month_9.0','Month_10.0','Month_11.0','Month_12.0',
           'SchoolHoliday','Year_1.0','Year_2.0','Year_3.0']

print('Loading data ...')
data_dir = '../../data/'
hdf = HDFStore(data_dir + 'data.h5')
data_train = hdf['data_train']
data_test = hdf['data_test']
data_train['Date'] = pd.to_datetime(data_train.Date)
data_train = data_train.ix[pd.to_datetime(data_train.Date).order().index]
(DataTr, DataTe) = train_test_split(data_train,0.00)

in_neurons = len(columns)
hidden_neurons = 300
hidden_neurons_2 = 300
out_neurons = 1
nb_epoch = 10
evaluation = []

print ('Creating simple DLSTM ...')
model = Sequential()
model.add(LSTM(in_neurons, hidden_neurons, return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(hidden_neurons, hidden_neurons_2, return_sequences=False))
model.add(Dropout(0.3))
model.add(Dense(hidden_neurons_2, out_neurons, init='uniform'))
model.compile(loss='mean_squared_error', optimizer='rmsprop')

# if we have some store model continue with that
if os.path.exists('lstm_simple_weights'):
    print ('Continue with saved model ...')
    model.load_weights('lstm_simple_weights')

print ('Getting data ...')
stores = DataTr['Store'].unique()

print ('Fitting model ...')
for epoch in range(10):
    shuffle(stores)
    for store in stores:
        print ('Epoch:', epoch,' Store:', store)
        data = DataTr[DataTr.Store == store]
        # get max 10 day sequence window
        x, y = get_data_sequence(data,columns,n_prev=7)
        print ('Evaluation loss before:', model.evaluate(x,y,verbose=2))
        model.fit(x, y, validation_split=0.00, batch_size=4,shuffle=True,nb_epoch=2,verbose=2)
        model.save_weights('lstm_simple_weights', overwrite=True)
        print ('---------')


print ('Done ...')
#X_train, Y_train = None, None
#X_test = get_test_dataset_simple(data_test)
#predicted_values = model.predict(X_test)
#data_result = pd.DataFrame({'Sales': predicted_values.astype(int).flatten(), 'Id': data_test['Id'].tolist()})
#store_results(data_result, 'test_output.csv')
