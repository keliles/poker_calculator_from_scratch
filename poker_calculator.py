import pandas as pd
import numpy as np
from itertools import combinations, groupby
import warnings


warnings.simplefilter(action='ignore', category=FutureWarning)

all_cards = ['As','2s','3s','4s','5s','6s','7s','8s','9s','Ts','Js','Qs','Ks',
	     'Ac','2c','3c','4c','5c','6c','7c','8c','9c','Tc','Jc','Qc','Kc',
	     'Ah','2h','3h','4h','5h','6h','7h','8h','9h','Th','Jh','Qh','Kh',
	     'Ad','2d','3d','4d','5d','6d','7d','8d','9d','Td','Jd','Qd','Kd']

which_street = input('\nexample: "ten of spades, jack of diamonds, queen of hearts" = TsJdQh\nwhich cards are on the board already? (press enter if none)  ')
number_of_opponents = int(input('\nhow many opponents are there? (must be > 0) '))
know_opponent_cards = input('\ndo you know your opponents\' cards?(yes/no)  ')
if know_opponent_cards == 'yes':
	opponent_hands = pd.Series()
	for i in range(number_of_opponents):
		if i == 0:
			opponent_hands[i] = input(f'\nboard is {which_street}\ncards of opponent #{i + 1}:  ')
		else:
			opponent_hands[i] = input(f'cards of opponent #{i + 1}:  ')
	user_cards = input('\nwhat cards do you have?  ')
if know_opponent_cards == 'no':
	opponent_hands = None
	user_cards = input('\nwhat cards do you have?  ')
print('thinking...')

hand_rankings = {1: "Straight Flush",
		 2: "Quads",
		 3: "Full House",
		 4: "Flush",
		 5: "Straight",
		 6: "Set",
		 7: "Two Pair",
		 8: "Pair",
		 9: "High Card"}

card_rankings = {1:'A',
		 2:'K',
		 3:'Q',
		 4:'J',
		 5:'T',
		 6:'9',
		 7:'8',
		 8:'7',
		 9:'6',
		10:'5',
		11:'4',
		12:'3',
		13:'2'}

def separate_cards(card_group):
	cards = [card_group[i:i+2] for i in range(0,len(str(card_group)),2)]
	return cards

if which_street != '':
	board_and_user = which_street + user_cards
else:
	board_and_user = user_cards
if opponent_hands is not None:
	board_and_opponents = {}
	for i in range(len(opponent_hands)):
		board_and_opponents[i] = which_street + opponent_hands[i]
else: 
	board_and_opponents = ''
	board_and_user = which_street + user_cards

if board_and_opponents != '':
	separate_board_and_opponents = {}
	for i in range(len(board_and_opponents)):
		separate_board_and_opponents[i] = separate_cards(board_and_opponents[i])
if opponent_hands is not None:
	separate_opponents = {}
	for i in range(len(opponent_hands)):
		separate_opponents[i] = separate_cards(opponent_hands[i])
else:
	separate_opponents = ''
separate_user = separate_cards(user_cards)

remaining_cards = list(set(all_cards) - set(
    separate_user +
    sum([separate_opponents[i] for i in separate_opponents], []) +
    (separate_cards(which_street) if which_street != '' else [])
))

possible_straights = [['A','2','3','4','5'],
		      ['2','3','4','5','6'],
		      ['3','4','5','6','7'],
		      ['4','5','6','7','8'],
		      ['5','6','7','8','9'],
		      ['6','7','8','9','T'],
		      ['7','8','9','T','J'],
		      ['8','9','T','J','Q'],
		      ['9','T','J','Q','K'],
		      ['T','J','Q','K','A']]

def is_straight(hand):
	hand_numbers = list(hand[::2])
	straight_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank'])
	for possible_straight in possible_straights:
		if set(possible_straight).issubset(set(hand_numbers)):
			straight_info['is'] = True
			straight_info['rank'] = 5
			for rank, card in card_rankings.items():
				if card == possible_straight[0]:
					if pd.isna(straight_info['subrank']):
						straight_info['subrank'] = rank
					else:
						if rank < straight_info['subrank']:
							straight_info['subrank'] = rank
	return straight_info

def is_flush(hand):
	flush_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank','suit'])
	hand_suits = ''.join(map(str, hand[1::2]))
	grouped_suits = [list(group) for key, group in groupby(sorted(hand))]
	for suit_group in grouped_suits:
		if len(suit_group) >= 5:
			flush_info['is'] = True
			flush_info['rank'] = 4
			flush_info['suit'] = suit_group[0]
	if not pd.isna(flush_info['is']):
		hand_numbers = set(list(hand[::2]))
		for number in hand_numbers:
			for rank, card in card_rankings.items():
				if card == number:
					if pd.isna(flush_info['subrank']):
						flush_info['subrank'] = rank
					else:
						if rank < flush_info['subrank']:
							flush_info['subrank'] = rank
	return flush_info
					
def is_straight_flush(hand):
	SF_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank','suit'])
	straight = is_straight(hand)
	flush = is_flush(hand)
	hand_suits = list(hand[1::2])
	if flush['is'] and straight['is']:
		straight_cards = []
		suit = flush['suit']
		separated_hand = separate_cards(hand)
		for card in separated_hand:
			if card[1] == suit:
				straight_cards.append(card)
		joined_straight_cards = ''.join(map(str, straight_cards))
		straight_card_numbers = list(joined_straight_cards[::2])
		for possible_straight in possible_straights:
			if set(possible_straight).issubset(set(straight_card_numbers)):
				SF_info['is'] = True
				SF_info['rank'] = 1
				SF_info['subrank'] = straight['subrank']
				SF_info['suit'] = flush['suit']
	return SF_info

def is_full_house(hand):
	FH_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	three_group = False
	two_group = False
	for group in grouped_numbers:
		if len(group) == 2:
			two_group = True
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(FH_info['microrank']):
						FH_info['microrank'] = rank
					else:
						if rank < FH_info['microrank']:
							FH_info['microrank'] = rank
		if len(group) == 3:
			three_group = True
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(FH_info['subrank']):
						FH_info['subrank'] = rank
					else:
						if rank < FH_info['subrank']:
							FH_info['subrank'] = rank
	if three_group and two_group:
		FH_info['is'] = True
		FH_info['rank'] = 3
	else:
		FH_info['subrank'] = np.nan
		FH_info['microrank'] = np.nan
	return FH_info

def is_quads(hand):
	Q_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	for group in grouped_numbers:
		if len(group) == 4:
			Q_info['is'] = True
			Q_info['rank'] = 2
			for number in hand_numbers:
				if number != group[0]:
					for rank, card in card_rankings.items():
						if card == number:
							if pd.isna(Q_info['subrank']):
								Q_info['subrank'] = rank
							else:
								if rank < Q_info['subrank']:
									Q_info['subrank'] = rank
	return Q_info

def is_set(hand):
	set_info = pd.Series(index=['is','rank','subrank','microrank','minirank','tinyrank','supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	for group in grouped_numbers:
		if len(group) == 3:
			set_info['is'] = True
			set_info['rank'] = 6
			for number in hand_numbers:
				if number != group[0]:
					for rank, card in card_rankings.items():
						if card == number:
							if pd.isna(set_info['subrank']):
								set_info['subrank'] = rank
							else:
								if rank < set_info['subrank']:
									set_info['subrank'] = rank
	return set_info

def is_two_pair(hand):
	TP_info = pd.Series(index=['is','rank','subrank','microrank','minirank', 'tinyrank', 'supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	pair_group = []
	for group in grouped_numbers:
		if len(group) == 2:
			pair_group.append(group)
	top_pair = ''
	second_pair = ''
	if len(pair_group) >= 2:
		TP_info['is'] = True 
		TP_info['rank'] = 7
		for pair in pair_group:
			for rank, card in card_rankings.items():
				if card == pair[0]:
					if pd.isna(TP_info['subrank']):
						TP_info['subrank'] = rank
						top_pair = pair
					else:
						if rank < TP_info['subrank']:
							TP_info['subrank'] = rank
							top_pair = pair
		pair_group.remove(top_pair)
		for pair in pair_group:
			for rank, card in card_rankings.items():
				if card == pair[0]:
					if pd.isna(TP_info['microrank']):
						TP_info['microrank'] = rank
						second_pair = pair
					else:
						if rank < TP_info['microrank']:
							TP_info['microrank'] = rank
							second_pair = pair
		grouped_numbers.remove(top_pair)
		grouped_numbers.remove(second_pair)
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(TP_info['minirank']):
						TP_info['minirank'] = rank
					else:
						if rank < TP_info['minirank']:
							TP_info['minirank'] = rank
	return TP_info

def is_pair(hand):
	pair_info = pd.Series(index=['is','rank','subrank','microrank','minirank', 'tinyrank', 'supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	pair_group = []
	for group in grouped_numbers:
		if len(group) == 2:
			pair_group.append(group)
	top_pair = ''
	if len(pair_group) == 1:
		pair_info['is'] = True
		pair_info['rank'] = 8
		for pair in pair_group:
			for rank, card in card_rankings.items():
				if card == pair[0]:
					if pd.isna(pair_info['subrank']):
						pair_info['subrank'] = rank
						top_pair = pair
					else:
						if rank < pair_info['subrank']:
							pair_info['subrank'] = rank
							top_pair = pair
		grouped_numbers.remove(top_pair)
		top_kicker = ''
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(pair_info['microrank']):
						pair_info['microrank'] = rank
						top_kicker = card
					else:
						if rank < pair_info['microrank']:
							pair_info['microrank'] = rank
							top_kicker = card
		grouped_numbers.remove(list(str(top_kicker)))
		second_kicker = ''
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(pair_info['minirank']):
						pair_info['minirank'] = rank
						second_kicker = group[0]
					else:
						if rank < pair_info['minirank']:
							pair_info['minirank'] = rank
							second_kicker = group[0]
		grouped_numbers.remove(list(str(second_kicker)))
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					if pd.isna(pair_info['tinyrank']):
						pair_info['tinyrank'] = rank
					else:
						if rank < pair_info['tinyrank']:
							pair_info['tinyrank'] = rank
	return pair_info

def is_high_card(hand):
	HC_info = pd.Series(index=['is','rank','subrank','microrank','minirank', 'tinyrank', 'supersmallrank'])
	hand_numbers = ''.join(map(str, hand[::2]))
	grouped_numbers = [list(group) for key, group in groupby(sorted(hand_numbers))]
	SF = is_straight_flush(hand)
	Q = is_quads(hand)
	FH = is_full_house(hand)
	Flush = is_flush(hand)
	Straight = is_straight(hand)
	TP = is_two_pair(hand)
	Pairs = is_pair(hand)
	if pd.isna(SF['is'] and Q['is'] and FH['is'] and Flush['is'] and Straight['is'] and TP['is'] and Pairs['is']):
		HC_info['is'] = True
		HC_info['rank'] = 9
		top_card = ''
		for number in hand_numbers:
			for rank, card in card_rankings.items():
				if card == number:
					if pd.isna(HC_info['subrank']):
						HC_info['subrank'] = rank
						top_card = number
					else:
						if rank < HC_info['subrank']:
							HC_info['subrank'] = rank
							top_card = number
		grouped_numbers.remove(list(str(top_card)))
		top_kicker = ''
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					HC_info['microrank'] = rank
					top_kicker = group[0]
				else:
					if rank < HC_info['microrank']:
						HC_info['microrank'] = rank
						top_kicker = group[0]
		grouped_numbers.remove(list(str(top_kicker)))
		second_kicker = ''
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					HC_info['minirank'] = rank
					second_kicker = group[0]
				else:
					if rank < HC_info['minirank']:
						HC_info['minirank'] = rank
						second_kicker = group[0]
		grouped_numbers.remove(list(str(second_kicker)))
		third_kicker = ''
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					HC_info['tinyrank'] = rank
					third_kicker = group[0]
				else:
					if rank < HC_info['tinyrank']:
						HC_info['tinyrank'] = rank
						third_kicker = group[0]
		grouped_numbers.remove(list(str(third_kicker)))
		for group in grouped_numbers:
			for rank, card in card_rankings.items():
				if card == group[0]:
					HC_info['supersmallrank'] = rank
				else:
					if rank < HC_info['supersmallrank']:
						HC_info['supersmallrank'] = rank
	return HC_info

board_and_opponents_list = []
if board_and_opponents:
	for key, item in board_and_opponents.items():
		board_and_opponents_list.append(item)
all_hands = [board_and_user]
for opponent_hand in board_and_opponents_list:
	all_hands.append(opponent_hand)

def sim(hand_list):
	remaining_streets = 7 - (int(len(hand_list[0])) / 2)
	sim_count = 0
	win_tally = pd.Series()
	for player in range(len(hand_list)):
		win_tally[str(player)] = 0
	for combo in combinations(remaining_cards,(int(remaining_streets))):
		current_hand = 0
		hand_bank = pd.Series()
		for hand in hand_list:
			hand_id = np.nan
			sim_hand = hand + (''.join(map(str,list(combo))))
			print(f'\nhand to be ranked: {sim_hand}\n')
			Straight_Flush = is_straight_flush(sim_hand)
			if not np.isnan(Straight_Flush['is']):
				hand_id = Straight_Flush
				print(f'player #{current_hand} has a straight flush!')
			else:
				Quads = is_quads(sim_hand)
				if not np.isnan(Quads['is']):
					hand_id = Quads
					print(f'player #{current_hand} has quads!')
				else:
					Full_House = is_full_house(sim_hand)
					if not np.isnan(Full_House['is']):
						hand_id = Full_House
						print(f'player #{current_hand} has a full house!')
					else:
						Flush = is_flush(sim_hand)
						if not np.isnan(Flush['is']):
							hand_id = Flush
							print(f'player #{current_hand} has a flush!')
						else:
							Straight = is_straight(sim_hand)
							if not np.isnan(Straight['is']):
								hand_id = Straight
								print(f'player #{current_hand} has a straight!')
							else:
								Set = is_set(sim_hand)
								if not np.isnan(Set['is']):
									hand_id = Set
									print(f'player #{current_hand} has a set!')
								else:
									Two_Pair = is_two_pair(sim_hand)
									if not np.isnan(Two_Pair['is']):
										hand_id = Two_Pair
										print(f'player #{current_hand} has two pair!')
									else:
										Pair = is_pair(sim_hand)
										if not np.isnan(Pair['is']):
											hand_id = Pair
											print(f'player #{current_hand} has a pair!')
										else:
											High_Card = is_high_card(sim_hand)
											if not np.isnan(High_Card['is']):
												hand_id = High_Card
												print(f'player #{current_hand} has a high card!')
			hand_bank[f'{current_hand}'] = hand_id
			current_hand += 1
		winner = np.nan
		round_counter = 1
		threshold = len(hand_list) - 1
		for player, hand_id in hand_bank.items():
			if pd.isna(winner):
				winner = player
				rank = hand_id['rank']
				subrank = hand_id['subrank']
				microrank = hand_id['microrank']
				minirank = hand_id['minirank']
				tinyrank = hand_id['tinyrank']
				supersmallrank = hand_id['supersmallrank']
				continue
			else:
				if hand_id['rank'] < rank:
					rank = hand_id['rank']
					subrank = hand_id['subrank']
					microrank = hand_id['microrank']
					minirank = hand_id['minirank']
					winner = player
				else: 
					if hand_id['rank'] == rank:
						if hand_id['subrank'] < subrank:
							winner = player
							rank = hand_id['rank']
							subrank = hand_id['subrank']
							microrank = hand_id['microrank']
							minirank = hand_id['minirank']
						else:
							if hand_id['subrank'] == subrank:
								if not pd.isna(hand_id['microrank']):
									if hand_id['microrank'] < microrank:
										winner = player
										rank = hand_id['rank']
										subrank = hand_id['subrank']
										microrank = hand_id['microrank']
										minirank = hand_id['minirank']
									else:
										if hand_id['microrank'] == microrank:
											if not pd.isna(hand_id['minirank']):
												if hand_id['minirank'] < minirank:
													winner = player
													rank = hand_id['rank']
													subrank = hand_id['subrank']
													microrank = hand_id['microrank']
													minirank = hand_id['minirank']
											else: 
												if hand_id['minirank'] == minirank:
													if not pd.isna(hand_id['tinyrank']):
														if hand_id['tinyrank'] < tinyrank:
															winner = player
															rank = hand_id['rank']
															subrank = hand_id['subrank']
															microrank = hand_id['microrank']
															minirank = hand_id['minirank']
															tinyrank = hand_id['tinyrank']
															supersmallrank = hand_id['supersmallrank']
														else:
															if hand_id['tinyrank'] == tinyrank:
																if not pd.isna(hand_id['supersmallrank']):
																	if hand_id['supersmallrank'] < supersmallrank:
																		winner = player
																		rank = hand_id['rank']
																		subrank = hand_id['subrank']
																		microrank = hand_id['microrank']
																		minirank = hand_id['minirank']
																		tinyrank = hand_id['tinyrank']
																		supersmallrank = hand_id['supersmallrank']
																else:
																	winner = np.nan
																	print(f'no supersmallrank...winner is {winner}')
																	rank = np.nan
																	subrank = np.nan
																	microrank = np.nan
																	minirank = np.nan
													else:
														winner = np.nan
														print(f'no tinyrank...winner is {winner}')
														rank = np.nan
														subrank = np.nan
														microrank = np.nan
														minirank = np.nan
												else:
													winner = np.nan
													print(f'no minirank...winner is {winner}')
													rank = np.nan
													subrank = np.nan
													microrank = np.nan
													minirank = np.nan
								else:
									winner = np.nan
									print(f'no microrank...winner is {winner}')
									rank = np.nan
									subrank = np.nan
									microrank = np.nan
									minirank = np.nan
				if not pd.isna(winner):
					if round_counter == threshold:
							win_tally[winner] += 1
							sim_count += 1
				round_counter += 1
			print(f'\nwinner: {winner}')
			print(f'their hand:\n{hand_id}\n:')
	win_percentages = win_tally / sim_count
	win_percentages['tie'] = 1 - win_percentages.sum()
	return win_percentages
result = sim(all_hands)
result = result.rename({'0': 'user'})
print(f'\n\ngiven a board of: {which_street}')
print(f'\nwhere...\nuser has: {user_cards}')
if opponent_hands is not None:
	for i in range(len(opponent_hands)):
		print(f'opponent #{i+1} has: {opponent_hands[i]}')
print(f'\neach player\'s probability of winning is:\n{result}')
