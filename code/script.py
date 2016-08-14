import sys
import getopt
import csv
import itertools
from tabulate import tabulate

matchups_by_week = [];
confirmed = [];
denied = [];
guys_map = {};
girls_map = {};

def main(argv):
	week = None;
	try:
		opts, args = getopt.getopt(argv,"hw:",["week="]);
	except getopt.GetoptError:
		print "USAGE: solver.py -w <week number>";
		sys.exit(2);
	for opt, arg in opts:
		if opt == '-h':
			print 'USAGE: solver.py -w <week number>'
			sys.exit();
		elif opt in ("-w", "--week"):								
			week = int(arg);

	with open("data/guys.csv", "rb") as guys_file, open("data/girls.csv", "rb") as girls_file, open("data/matchups.csv", "rb") as match_file, open("data/truthbooth.csv", "rb") as tb_file:
		guys = next(csv.reader(guys_file));
		girls = next(csv.reader(girls_file));
		for i in range(len(guys)):
			guys_map[guys[i]] = i;
			girls_map[girls[i]] = i;

		matchup_reader = csv.reader(match_file);
		tb_reader = csv.reader(tb_file);
		next(tb_reader, None);
		next(matchup_reader, None);
		
		count = 0;
		for matchup in matchup_reader:
			count += 1;
			if week is not None:
				if count > week:
					break;
			matchups_by_week.append((matchup[1:11], int(matchup[11])));
		
		count = 0;
		for tb_result in tb_reader:
			count += 1;
			if week is not None:
				if count > week:
					break;
			if int(tb_result[2]):
				confirmed.append((tb_result[0], tb_result[1]));
			else:
				denied.append((tb_result[0], tb_result[1]));

		valid_possibilities = [];
		for possibility in itertools.permutations(girls, len(girls)):
			if check_week_matchups(possibility) and check_tb(possibility):
				valid_possibilities.append(possibility);

		percentages = [[0.0 for i in range(10)] for i in range(10)];
		for valid_match in valid_possibilities:
			for i in range(len(valid_match)):
				percentages[i][girls_map[valid_match[i]]] = percentages[i][girls_map[valid_match[i]]] + 1.0;
		for i in range(len(percentages)):
			for j in range(len(percentages[i])):
				if percentages[i][j] == 0.0:
					percentages[i][j] = "X";
				else:
					percentages[i][j] = 100 * percentages[i][j] / float(len(valid_possibilities));
			percentages[i] = [guys[i]] + percentages[i];

		percentages = [[""] + girls] + percentages;
		print tabulate(percentages, floatfmt=".1f", tablefmt="fancy_grid");

def check_tb(possible_combo):
	for guy, girl in confirmed:
		if possible_combo[guys_map[guy]] != girl:
			return False;
	for guy, girl in denied:
		if possible_combo[guys_map[guy]] == girl:
			return False;
	return True;

def check_week_matchups(possible_combo):
	for week_result, num_matches in matchups_by_week:
		if overlap(possible_combo, week_result) != num_matches:
			return False;
	return True;

def overlap(possible_combo, week_result):
	count = 0;
	for i in range(len(possible_combo)):
		if possible_combo[i] == week_result[i]:
			count += 1;
	return count;

if __name__ == "__main__":
	main(sys.argv[1:]);
