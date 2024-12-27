# -*-coding:Utf-8 -*

#https://www.digitalocean.com/community/tutorials/how-to-compare-two-lists-in-python

def are_list_equals(list1, list2):
    l1_sorted = sorted(list1)
    l2_sorted = sorted(list2)
    return l1_sorted == l2_sorted
