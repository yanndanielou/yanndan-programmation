# -*-coding:Utf-8 -*

#https://www.digitalocean.com/community/tutorials/how-to-compare-two-lists-in-python

def are_list_equals(list1:list, list2:list):
    l1_sorted = sorted(list1)
    l2_sorted = sorted(list2)
    return l1_sorted == l2_sorted


#https://www.geeksforgeeks.org/python-check-if-a-list-is-contained-in-another-list/

#Approach #1: Naive Approach 
def is_list_included_in_second_list(list1:list, list2:list):

    pass



#Approach #1: Naive Approach 
def are_all_elements_of_list_included_in_list(list1:list, list2:list):
    return set(list1) <= set(list2)
