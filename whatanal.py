import re
import csv
import collections as coll


class Chat():
    def __init__(self, filename, fena=''):
        self.filename = filename
        self.fena = fena
        self.chat = open(filename, encoding="utf8")

    def __get_num_of_date(self, date):
        ''' Finds a number between slashes
            Returns the number and the string stripped of that number
        '''
        if date[1] == '/':
            num = int(date[:1])
            date = date[2:]
        else:
            num = int(''.join(date[:2]))
            date = date[3:]
        return date, num

    def __get_date(self, line):
        ''' Finds the date of a whatsapp message
            Returns the day, the month and the year separately as integers (DD/MM/YY format)
        '''
        end_date = re.search('[0-9][0-9],', line).span()[0] + 2
        date = line[:end_date]
        date, month = self.__get_num_of_date(date)
        date, day = self.__get_num_of_date(date)
        date, year = self.__get_num_of_date(date)
        return day, month, year

    def __get_author(self, line):
        ''' Finds the author of a given line (using whatsapp formatting)
            Returns the name of the author and the starting and ending indexes of
            the name inside the line
        '''
        start = re.search('(A|P)M - [A-Z]', line).span()[1] - 1
        end = re.search(':', line[start:].strip()).span()[1] + start - 1
        return line[start:end], start, end

    def members(self):
        ''' Counts the number of messages per member of the chat.
            Returns a dictionary with each member as key
        '''
        members = dict()
        for line in self.chat:
            try:
                key = self.__get_author(line)[0]
                if key == self.fena:
                    continue
                members[key] = members.get(key, 0) + 1
            except BaseException:
                continue
        self.chat.seek(0)
        return members

    def hours(self):
        ''' Counts the number of messages in each hour for the given chat
            Returns a dictionary with each hour (24h format, midnight is 24) as key
        '''
        hours = dict()
        for line in self.chat:
            try:
                author, start = self.__get_author(line)[:2]
                if author == self.fena:
                    continue
                start -= 11
                key = int(line[start:start + 2])
                if key != 12 and 'P' in line[start + 6:start + 10]:
                    key += 12
                elif key == 12 and 'A' in line[start + 6:start + 10]:
                    key += 12
                hours[key] = hours.get(key, 0) + 1
            except BaseException:
                continue
        self.chat.seek(0)
        return hours

    def date(self):
        ''' Counts the number of messages in each day, month, year for the given
            chat.
            Returns 3 dictionaries, the months one has abbreviated month names as
            keys instead of numbers (e.g. 'JAN')
        '''

        days = dict()
        months = coll.OrderedDict([
            ('JAN', 0),
            ('FEB', 0),
            ('MAR', 0),
            ('APR', 0),
            ('MAY', 0),
            ('JUN', 0),
            ('JUL', 0),
            ('AUG', 0),
            ('SEP', 0),
            ('OCT', 0),
            ('NOV', 0),
            ('DEC', 0)])
        years = dict()
        for line in self.chat:
            try:
                if self.__get_author(line)[0] == self.fena:
                    continue
                day, month, year = self.__get_date(line)
                key = months_names[month - 1]
                months[key] += 1
                days[day] = days.get(day, 0) + 1
                years[year] = years.get(year, 0) + 1
            except BaseException:
                continue
        self.chat.seek(0)
        return days, months, years

    def longest(self):
        ''' Finds the longest message in the given chat and returns the message and
            its corresponding date (DD/MM/YY format)
        '''
        longest = ''
        longest_date = '1/1/01'
        for line in self.chat:
            try:
                if self.__get_author(line)[0] == self.fena:
                    continue
                start = re.search('(A|P)M - [A-Z]', line).span()[1]
                end = re.search(':', line[start:].strip()).span()[
                    1] + start + 1
                temp = line[end:]
                if len(temp) > len(longest):
                    longest = temp
                    day, month, year = self.__get_date(line)
                    longest_date = str(day) + '/' + \
                        str(month) + '/' + str(year)
                    print(longest_date)
            except BaseException:
                continue
        self.chat.seek(0)
        return longest, longest_date.strip()

    def average_chars(self):
        ''' Finds the average number of characters per message per each member.
            Returns a dictionary with members as keys
        '''
        avg_len = dict()
        length = dict()
        authors = self.members()
        self.chat.seek(0)
        for line in self.chat:
            for author in authors:
                try:
                    key, start, end = self.__get_author(line)
                    if key == author:
                        length[key] = length.get(key, 0) + len(line[end:])
                except BaseException:
                    continue
        for i in length:
            avg_len[i] = round(length[i] / authors[i], 1)
        self.chat.seek(0)
        return avg_len

    def average_words(self):
        ''' Finds the average number of words per message per each member.
            Returns a dictionary with members as keys
        '''
        avg_num = dict()
        nums = dict()
        authors = self.members()
        self.chat.seek(0)
        for line in self.chat:
            for author in authors:
                try:
                    key = self.__get_author(line)[0]
                    if key == author:
                        nums[key] = nums.get(key, 0) + \
                            len(re.findall(r'\w+', line))
                except BaseException:
                    continue
        for i in nums:
            avg_num[i] = round(nums[i] / authors[i], 1)
        self.chat.seek(0)
        return avg_num

    def msg_evolution(self):
        ''' Finds the number of messages per month per each member.
            Returns a dictionary with the members as key and a dictionary with the
            months (format MM/YY) as keys as values
        '''
        evolution = dict()
        authors = self.members()
        self.chat.seek(0)
        for author in authors:
            evolution[author] = dict()
        for line in self.chat:
            try:
                month, year = self.__get_date(line)[1:]
                date_str = '/'.join([str(month), str(year)])
                for person in evolution:
                    if person == self.__get_author(line)[0]:
                        evolution[person][date_str] += 1
                    elif not evolution[person].get(date_str):
                        evolution[person][date_str] = 0
            except BaseException:
                continue
        self.chat.seek(0)
        return evolution


def export_csv(
        file,
        dictionary,
        header1='Members',
        header2='Values'):
    with open('csvs/' + file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([header1, header2])
        for i in dictionary:
            writer.writerow([i, dictionary[i]])
