import csv


def main():
    csvfile = open('../../Library/Keywords/Java_papers_keywords_top10.csv', newline='', encoding='UTF-8')
    readCSV = csv.DictReader(csvfile)
    for row in readCSV:
        print(row)


main()
