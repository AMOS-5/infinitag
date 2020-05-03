import pre_processing
import sys


#obj2 = pre_processing.MyNLP('D:\Data Sciences\Ramya\I2B2Text\TextFiles\Train-Set2')
obj = pre_processing.MyNLP(sys.argv[1])
obj.lda()
