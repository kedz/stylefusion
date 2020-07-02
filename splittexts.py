from pycorenlp import StanfordCoreNLP
from collections import OrderedDict

Cf = [["although"], ["since"], ["in", "addition", "to"], ["aside", "from"]]
Cs = [
    [",",  "because"],  
    ["because",],  
    ["hence"],  
    [",",  "while"],  
    ["whereas"], 
    [",", "although"],
    ["and", "although"], 
    ["although"],
    ["unless"],
    [",", "now that"], 
    ["now", "that"],
    ["so", "that"], 
    [",", "so", "that"],
    ["meaning"],
    [",", "meaning"],
]

verbs = set(["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"])
rel_pron = ['who', 'which', 'whose', 'whom']

def check_match(s, p, i):
    sub_s = s[i:i+len(p)]
    return sub_s == p

def check_forward_connective(s):
    tokens = [t['word'].lower() for t in s['tokens']]
    n = len(tokens)
    i = 0
    for c in Cf:
        if check_match(tokens, c, i) and "," in tokens[i+len(c):]:
            j = i + len(c) + tokens[i+len(c):].index(",")
            return c, j
        

def apply_forward_connective(s, c,comma_idx):
    prefix = s['tokens'][len(c):comma_idx]
    suffix = s['tokens'][comma_idx+1:]
    
    prefix = "".join([x['before'] + x['originalText'] for x in prefix]).strip()
    suffix = "".join([x['before'] + x['originalText'] for x in suffix]).strip()
    prefix = prefix[0].upper() + prefix[1:] + "."
    suffix = suffix[0].upper() + suffix[1:]

    return ("forward connective", " ".join(c)), prefix, suffix

def check_intrasentence_connective(s):
    tokens = [t['word'].lower() for t in s['tokens']]
    n = len(tokens)
    for i in range(n):
        for c in Cs:
            if check_match(tokens, c, i):
                return c, i
     
def apply_intrasentence_connective(s, con, con_idx):
    prefix = "".join([x['before'] + x['originalText'] 
                      for x in s['tokens'][:con_idx]])
    prefix = prefix.strip()
    prefix = prefix[0].upper() + prefix[1:] + "."

    suffix = "".join([x['before'] + x['originalText']
                      for x in s['tokens'][con_idx + len(con):]])
    suffix = suffix.strip()
    suffix = suffix[0].upper() + suffix[1:]

    return (("intra-sentence connective", " ".join(con)), prefix, suffix)

def check_cataphora(s):
    pos = (s['tokens'][0]['pos'])

    #for d in s['basicDependencies']:
    #    print(d)

    label = [x['dep'] for x in s['basicDependencies'] if x['dependent'] == 1][0]
    if pos != "VBG" or label != "advcl":
        return
    comma_idx = None
    for i, token in enumerate(s['tokens']):
        if token['originalText'] == ',':
            comma_idx = i
            break
    if comma_idx is None:
        return 
    if s['tokens'][comma_idx + 2]['pos'] in verbs:
        return (comma_idx,)

def apply_cataphora(s, comma_idx):
    suffix = "".join([x['before'] + x['originalText'] 
                      for x in s["tokens"][comma_idx+1:]])
    suffix = suffix.strip()
    suffix = suffix[0].upper() + suffix[1:]

    prefix = "".join([x['before'] + x['originalText'] 
                      for x in s['tokens'][1:comma_idx]])
    prefix = prefix.strip() + "."
    subj = s['tokens'][comma_idx + 1]['originalText']
    verb = (s['tokens'][0]['originalText'][:-3] + 'ed').lower()
    prefix = f'{subj} {verb} {prefix}'
    prefix = prefix[0].upper() + prefix[1:]
        
    return (('cataphora',), prefix, suffix)

def check_conjunction(s):

    deps = sorted(s['basicDependencies'], key=lambda x: x['dependent'])
    assert len(deps) == len(set([x['dependent'] for x in deps]))

    n = len(deps)

    for i in range(n):
        if deps[i]['dep'] != 'cc':
            continue
        conj = None
        for j in range(i+1, min(i+6, n)):
            if deps[j]['dep'] == 'conj':
                conj = j
        if conj == None:
            continue
        for k in range(i+1, j):
            if deps[k]['dep'] in ['nsubj', 'nsubjpass']:
                return s['tokens'][i]['originalText'], i

def apply_conjunction(s, conj, conj_idx):
    prefix = ''.join([x['before'] + x['originalText'] 
                      for x in s['tokens'][:conj_idx]])
    prefix = prefix[0].upper() + prefix[1:]
    if prefix[-1] == ',':
        prefix = prefix[:-1]
    prefix = prefix + "."

    suffix = ''.join([x['before'] + x['originalText'] 
                      for x in s['tokens'][conj_idx + 1:]])
    suffix = suffix.strip()
    suffix = suffix[0].upper() + suffix[1:]
    return ("conjunction", conj), prefix, suffix

def check_apposition(s):
    deps = sorted(s['basicDependencies'], key=lambda x: x['dependent'])
    n = len(s['tokens'])
    for dep in s['basicDependencies']:
        if dep['dep'] == 'appos':
            k = dep['dependent']
            for i in range(k-1, -1, -1):
                if s['tokens'][i]['originalText'] == ',':
                    for j in range(k+1, n):
                        if s['tokens'][j]['originalText'] == ',':
                            if deps[i+1]['dep'] in ['det', 'poss']:
                                return i,j

        

def apply_apposition(s, start, stop):
    

    subj = ''.join([x['before'] + x['originalText'] for x in s['tokens'][:start]])
    appos = ''.join([x['before'] + x['originalText'] for x in s['tokens'][start+1:stop]]).strip()
    orig = ''.join([x['before'] + x['originalText'] for x in s['tokens'][stop+1:]]).strip()
    prefix = subj + " " + orig
    suffix = subj + " is " + appos + '.'
    
    return ("apposition",), prefix, suffix

def check_relative_clause(s):
    n = len(s['tokens'])
    for k, t in enumerate(s['tokens']):
        if t['originalText'] in rel_pron and k > 0:
            i = k - 1
            if s['tokens'][i]['originalText'] == ',':    
                for j in range(k+1, n):
                    if s['tokens'][j]['originalText'] == ',':
                        return (t['originalText'], i, j)

def apply_relative_clause(s, rp, i, j):
    subj = clean_span(s,0,i)
    rphrase = clean_span(s, i + 2, j)
    orig = clean_span(s, j+1, len(s['tokens']))

    prefix = fix_terminal_punctuation(f'{subj} {rphrase}' )
    suffix = f'{subj} {orig}'

    return ('relative_clause', rp), prefix, suffix

def fix_terminal_punctuation(x):
    if x[-1] in ",;":
        return x[:-1] + '.'
    else:
        return x + '.'

def clean_span(sent, i, j):
    toks = sent['tokens'][i:j]
    strings = [x['before'] + x['originalText'] for x in toks]
    return ''.join(strings).strip()

RULES = (
    ('forward connective', check_forward_connective, apply_forward_connective),
    ('intra-sentence connective', check_intrasentence_connective, apply_intrasentence_connective),
    ('cataphora', check_cataphora, apply_cataphora),
    ('conjunction', check_conjunction, apply_conjunction),
    ('relative clause', check_relative_clause, apply_relative_clause),
    ('apposition', check_apposition, apply_apposition),
)
ORD_RULES = OrderedDict()
for name, check, application in RULES:
    ORD_RULES[name] = {'check': check, 'apply': application}


class SplitTexts:
    def __init__(self, port):
        self._cnlp = StanfordCoreNLP(f'http://localhost:{port}')
   
    def preprocess(self, text):
        return self._cnlp.annotate(
            text, properties={
                'annotators': 'parse,lemma', 
                'outputFormat': 'json'})
 

    def apply_rules(self, text):
        data = self.preprocess(text)

        results = []

        for s in data['sentences']:
            rule_matched = False
            for name, rule in ORD_RULES.items():
                check = rule['check'](s)
                if check:
                    result = rule['apply'](s, *check)
                    results.append(result)
                    rule_matched = True
                    break
            if not rule_matched:
                results.append(
                    (None, ''.join([x['before'] + x['originalText'] for x in s['tokens']])))

        return results
            

