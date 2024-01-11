from recursivenamespace import rns

rn = rns()

# '-' in keys is converted to '_' in attributes
rn.scores = rns({'score-1': 98.4, 'score-2': 100})
print(f"rn.scores.score_1: {rn.scores.score_1}")
print(f"rn.scores.score_2: {rn.scores.score_2}")
rn.scores.score_3 = 99.07
print(f"rn.scores.score_3: {rn.scores.score_3}")

# '-' and '_' in keys are equivalent
print(rn.scores['score-1'] == rn.scores['score_1'])

