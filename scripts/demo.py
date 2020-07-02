from splittexts import SplitTexts
port = 9000
splitter = SplitTexts(port)


def print_rules(s):
    print("(original)")
    print("   ", s)
    for rule_result in splitter.apply_rules(s):
        rule_name = rule_result[0]
        if rule_name is not None:
            sentA, sentB = rule_result[1:]
            print(f"({rule_name})")
            print("   ", sentA)
            print("   ", sentB)
        else:
            print("(None)")
            print("   ", rule_result[1])
    print()

norule = "This sentence is atomic."
fwd_con1 = "Although the friendship somewhat healed years later, it was a devastating loss to Croly."
fwd_con2 = "Since you arrived, she is not sure this is the way."
fwd_con3 = "Aside from the light of systems and screens on all the walls, the interior of the command hub was darkened."
intra_con1 = "Open workouts are held every Sunday unless the gym is closed for a holiday or other special events."
intra_con2 = "It was recognized as the flu, although records describe conditions which were highly likely to have been polio."
cata_con1 = "Stating that the proponents were unlikely to succeed in this appeal, Walker rejected the stay request on October 23."
cata_con2 = "Comparing Logan's unconcerned response with Dr. Wynn's kindness, Deidre glared at the phone."
conj1 = "The time of the autumn floods came, and the hundred streams poured into the Yellow River."
appos1 = "The frigidarium, the last stop in the bath house, was where guests would cool off in a large pool."
relclause1 = 'Kubler, who retired from cycling in 1957, remained a revered figure in the wealthy alpine nation.'

print_rules(norule)
print_rules(fwd_con1)
print_rules(fwd_con2)
print_rules(fwd_con3)
print_rules(intra_con1)
print_rules(intra_con2)
print_rules(cata_con1)
print_rules(cata_con2)
print_rules(conj1)
print_rules(appos1)
print_rules(relclause1)


lot49 = "One summer afternoon Mrs. Oedipa Maas came home from a Tupperware party whose hostess had put perhaps too much kirsch in the fondue to find that she, Oedipa, had been named executor, or she supposed executrix, of the estate of one Pierce Inverarity, a California real estate mogul who had once lost two million dollars in his spare time but still had assets numerous and tangled enough to make the job of sorting it all out more than honorary."

print_rules(lot49)
print_rules("She supposed executrix, of the estate of one Pierce Inverarity, a California real estate mogul who had once lost two million dollars in his spare time but still had assets numerous and tangled enough to make the job of sorting it all out more than honorary.")


print_rules("Having placed in my mouth sufficient bread for three minutes' chewing, I withdrew my powers of sensual perception and retired into the privacy of my mind, my eyes and face assuming a vacant and preoccupied expression.")

print_rules("My own complete happiness, and the home-centred interests which rise up around the man who first finds himself master of his own establishment, were sufficient to absorb all my attention, while Holmes, who loathed every form of society with his whole Bohemian soul, remained in our lodgings in Baker Street, buried among his old books, and alternating from week to week between cocaine and ambition, the drowsiness of the drug, and the fierce energy of his own keen nature.")
