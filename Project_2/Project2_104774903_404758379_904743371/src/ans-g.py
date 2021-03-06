# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 15:51:23 2017

@author: swati.arora
"""

from sklearn.datasets import fetch_20newsgroups
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk import word_tokenize
import string
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import confusion_matrix, classification_report, roc_curve
from sklearn.metrics import auc
from sklearn.preprocessing import Normalizer
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

def stemList(stringList):
    stemmer = SnowballStemmer("english")
    data=[]
    punctuations = list(string.punctuation)
    punctuations.append("''")
    # Stem and Remove Punctuations in one go
    for s in stringList:
        data.append(' '.join([stemmer.stem(i.strip("".join(punctuations))) for i in word_tokenize(s) if i not in punctuations]))
    return data

# defining categories which need to be classified
categoriesToClassify =['comp.graphics', 'comp.os.ms-windows.misc', 
            'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware', 
            'rec.autos', 'rec.motorcycles', 'rec.sport.baseball', 
            'rec.sport.hockey']

# Fetching training and testing data
train_data = fetch_20newsgroups(subset='train', categories = categoriesToClassify, shuffle=True, random_state=42)

test_data = fetch_20newsgroups(subset='test', categories = categoriesToClassify, shuffle=True, random_state=42)


# Processing training dataset 
count_vect = CountVectorizer()
X_train_count_vector = count_vect.fit_transform(stemList(train_data.data))

#TF-IDF values for documents in training dataset
tf_transformer = TfidfTransformer(use_idf=True).fit(X_train_count_vector)
X_train_tfidf = tf_transformer.transform(X_train_count_vector)

# Dimensionality reduction using LSI to 50 features
svd = TruncatedSVD(n_components=50, random_state=42)
X_train = svd.fit_transform(X_train_tfidf)
X_train = Normalizer(copy=False).fit_transform(X_train)

# Target values
Y_train = train_data.target

# Merging the sub categories into one category to convert it to binary 
# classification problem
# 0 is for Computer technology
# 1 is for Recreational activity
for i in range(len(Y_train)):
    if(Y_train[i]<= 3):
        Y_train[i] = 0
    else:
        Y_train[i] = 1


# Processing test dataset
#TF-IDF values for documents in test dataset
X_test_counts = count_vect.transform(stemList(test_data.data))
tf_transformer = TfidfTransformer(use_idf=True).fit(X_test_counts)
X_test_tfidf = tf_transformer.transform(X_test_counts)

# Dimensionality reduction using LSI to 50 features
X_test = svd.transform(X_test_tfidf)
X_test = Normalizer(copy=False).fit_transform(X_test)

# Target values
Y_test = test_data.target

# Merging the sub categories into one category to convert it to binary 
# classification problem
# 0 is for Computer technology
# 1 is for Recreational activity      
for i in range(len(Y_test)):
    if(Y_test[i]<= 3):
        Y_test[i] = 0
    else:
        Y_test[i] = 1

# Naive Bayes classifier
naiveBayes_classifier = GaussianNB()
fit_model = naiveBayes_classifier.fit(X_train, Y_train)
Y_predicted = fit_model.predict(X_test)

# Metrics for model
print ("Confusion matrix \n")
print (confusion_matrix(Y_test, Y_predicted))
print ("\n")

print ("Recall and Precision score \n\n")
print (classification_report(Y_test, Y_predicted))
print ("\n")

print ("\nAccuracy : ", accuracy_score(Y_test, Y_predicted))

#ROC curve
probas_ = fit_model.predict_proba(X_test)                                    
fpr_bayes, tpr_bayes, thresholds = roc_curve(test_data.target, probas_[:, 1])
roc_auc_bayes = auc(fpr_bayes, tpr_bayes)
plt.plot(fpr_bayes, tpr_bayes, lw=1, color='red', label='ROC curve')
plt.plot([0, 1], [0, 1], color='navy', lw=1, linestyle='--')                                  
plt.xlim([-0.05, 1.05])
plt.ylim([-0.05, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Naive Bayes ROC Curve')
plt.legend(loc="lower right")
plt.show()
