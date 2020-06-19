# Arrange the available data based on the URN
# Auther: Yu Sun 
# Email: sunyu0410@gmail.com
# 18/06/2020
#
# Usage:
# python findMissingMod.py filename.txt
#   (the filename.txt is the file provided by Catherine)
#


import sys
import os
from pprint import pprint

# Read file
filename = sys.argv[1]
with open(filename, 'r') as f:
    c = f.readlines()

def extFactory(key, keyIndex, valIndex):
    '''Create functions to extract information for each line
    key: the text for the information, e.g. Modality;
    keyIndex: the index after str.split() for the label text;
    valIndex: the index after str.split() for the value;
    Returns the specific function
    '''
    def func(line):
        '''Extract the information for a given line.
        line: a string for one line in the file.
        Returns the information is presented, otherwise None.
        '''
        parts = line.strip().split('\t')
        return parts[valIndex] if len(parts) > valIndex and \
               parts[keyIndex] == key else None
    return func

extUrn = extFactory('URNumber', 1, 2)
extModality = extFactory('Modality', 5, 6)
extGrpNum = extFactory('GroupNumber', 5, 6)

def process(lines):
    '''Iterate through the lines and re-arrange the information
    lines: the list of lines returned by readlines().
    Returns a dictionary of group, modality sequences: 
        {urn: [group, modality, group, modality, ...]}
    '''
    # Final result to return
    result = {}
    # GroupNumber and Modality for one URN
    member = []
    for line in lines:
        # Extract the information
        modality = extModality(line)
        urn = extUrn(line)
        grp = extGrpNum(line)
        # Append GroupNumber and Modality to member
        if grp:
            member.append(int(grp))
        if modality:
            member.append(modality)
        # If a URN is present, store member in result and reset member
        if urn:
            assert urn not in result
            result[urn] = member
            member = []
    return result
    
def process2(r):
    '''Futher process the result returned by process().
    r: the result from process().
    Returns the rearranged result:
            {urn: {grp: [modalities], ...}}
    '''
    result2 = {}
    for urn in r:
        member = r[urn]
        member2 = {}
        length = len(member)
        # Make sure the length is an even number
        # Since it should be multiple (grp: modality) pairs
        assert length % 2 == 0
        for i in range(length//2):
            key = member[2*i]
            val = member[2*i+1]
            member2.setdefault(key, []).append(val)
        result2[urn] = member2
    return result2
    
def findMissing(r2, reqMod):
    '''Find the items that has missing modalities (defined by reqMod).
    r2: the re-arranged result returned by process2();
    reqMod: a list / set of required modalities (case-sensitive)
    Returns the items that has missing modalities:
        {urn: {grp: missing_mod}}
    '''
    reqMod = set(reqMod)
    r3 = {}
    for urn in r2:
        member2 = r2[urn]
        member3 = {}
        for grp in member2:
            modalities = set(member2[grp])
            diff = reqMod.difference(modalities)
            if diff:
                member3[grp] = list(diff)
        if member3:
            r3[urn] = member3
    return r3


r = process(c)
r2 = process2(r)
reqMod = ['CT', 'RTSTRUCT', 'RTPLAN', 'RTDOSE']
r3 = findMissing(r2, reqMod)

# Print the result
for urn in r3:
    print(urn)
    member3 = r3[urn]
    for key in sorted(member3.keys()):
        print('\t'+str(key))
        val = sorted(member3[key])
        for i in val:
            print('\t\t'+i)

