from import_export.formats import base_formats
import re
from enum import Enum

class RestrictionType(Enum):
    EVERYONE = '-1'
    CLASS = '-2'
    RACE = '-3'
    CABAL = '-4'
    PSALM = '-5'
    LEVEL = '51'

class GameHelpFileFormat:
    extensions = ('txt',)

    @classmethod
    def export_set(cls, dset):
        outputTxt = ''
        counter = 1
        for row in dset.dict:
            id = counter  # row.get('id')
            counter += 1
            restriction = row.get('restriction')
            restriction_type = row.get('restriction_type') + '~ ' if restriction in [RestrictionType.CLASS.value, RestrictionType.RACE.value, RestrictionType.CABAL.value, RestrictionType.PSALM.value] else ''
            keywords = ' '.join(["'" + k + "'" for k in row.get('keywords').split(',') if row.get('keywords')])
            # keywords = keywords + ' ' if keywords else ''
            keyword_main = "'" + row.get('keyword_main') + "'" + (' ' if keywords else '')
            syntax = '\n'.join(['Syntax: ' + s for s in row.get('syntax').split(',')]) + '\n' if row.get('syntax') else ''
            see_also = 'See also: ' + ', '.join(row.get('see_also').split(',')) + '\n' if row.get('see_also') else ''
            description = '\n' + row.get('description').replace('\\br ', '\n') + '\n\n' if row.get('description') else ''
            outputTxt += '#{id}\n{restriction} {restriction_type}{keyword_main}{keywords}~\n{keyword_main}\n{syntax}'\
            '{description}{see_also}~\n\n'.format(id=id, restriction=restriction, restriction_type=restriction_type,
            keywords=keywords, keyword_main=keyword_main, syntax=syntax, description=description, see_also=see_also)

        # add end of file mark
        outputTxt += '#0'

        return outputTxt
    
    @classmethod
    def import_set(cls, dset, in_stream):        
        dset.wipe()       
        dset.dict = cls._getRows(in_stream.getvalue())

    # @classmethod    
    # def _getHeaders(cls):
    #    headers = ['restriction', 'restriction_type', 'keyword_main', 'keywords', 'syntax', 'see_also', 'description', 'raw']
    #    return headers

    @classmethod
    def _getRows(cls, data):
        records = re.split(r'^\#[0-9]+', data, flags=re.MULTILINE)[1:] 

        rts = set({})
        parsedRecords = []
        allRecordsKeywords = set({})
        for r in records:
            r = r.strip()
            recordLines = r.splitlines()
            if not len(recordLines):
                continue

            # print(recordLines[0])

            # parse the restrictions line
            restrictionTypeRaw = re.match(r'^([-0-9]+)', recordLines[0]).group(0)
            if restrictionTypeRaw in ['-1', '0', '50', '-51']:
                restrictionType = RestrictionType.EVERYONE.value
            elif restrictionTypeRaw == '-2':
                restrictionType = RestrictionType.CLASS.value
            elif restrictionTypeRaw == '-3':
                restrictionType = RestrictionType.RACE.value
            elif restrictionTypeRaw == '-4':
                restrictionType = RestrictionType.CABAL.value
            elif restrictionTypeRaw == '-5':
                restrictionType = RestrictionType.PSALM.value
            elif int(restrictionTypeRaw) >= 51:
                #restrictionType = RestrictionType.LEVEL.name + ('60' if int(restrictionTypeRaw)>60 else restrictionTypeRaw)
                restrictionType = '60' if int(restrictionTypeRaw)>60 else restrictionTypeRaw
            else:
                continue
            rts.add(restrictionType)
            
            restrictionTypeSub = re.match(r'^' + restrictionTypeRaw + r'\s+([^~]*)~', recordLines[0]).group(1) if restrictionType in [RestrictionType.CLASS.value, RestrictionType.RACE.value, RestrictionType.CABAL.value, RestrictionType.PSALM.value] else ''
            recordLines[0] = recordLines[0].replace(restrictionTypeSub + '~', '') if restrictionType in [RestrictionType.CLASS.value, RestrictionType.RACE.value, RestrictionType.CABAL.value, RestrictionType.PSALM.value] else recordLines[0]

            keywords = []
            #keywordsStart = recordLines[0].find(restrictionTypeSub) + len(restrictionTypeSub)+1 if restrictionTypeSub != '' else len(restrictionTypeRaw)
            keywordsStart = len(restrictionTypeRaw)
            keywordsRaw = recordLines[0][keywordsStart:-1].strip()
            # Quote first keyword if not already
            if keywordsRaw and len(list(re.finditer(' ', keywordsRaw))) > 0 and keywordsRaw.strip()[0] != '\'':
                if keywordsRaw.strip().find('\'') > -1:
                    keywordsRaw = '\'' + keywordsRaw.strip()[0:keywordsRaw.strip().find('\'')-1] + '\'' + keywordsRaw.strip()[keywordsRaw.strip().find('\'')-1:]
            multiKeywordsRaw = re.findall(r'\'[^\']+\'', keywordsRaw)
            for k in multiKeywordsRaw:
                if k[1:-1] != "'":
                    keywords.append(k[1:-1])
                    keywordsRaw = keywordsRaw.replace(k, '')

            mainKeyword = None
            if len(keywords) > 0:
                singleKeywordsRaw = [x.strip() for x in keywordsRaw.split(' ') if x.strip() and x.strip() != "'" ]
            else:
                singleKeywordsRaw = [keywordsRaw]
                mainKeyword = keywordsRaw
            keywords += singleKeywordsRaw
            #remove duplicates if any
            keywords = list(dict.fromkeys(keywords))

            #if mainKeyword is None:
            #    mainKeywordMatch = re.match(r'^' + restrictionTypeRaw + r'\s+((\'[^\']+\')|([^\'][^\s~]+[\s~]))', recordLines[0])
            #    mainKeyword = mainKeywordMatch.group(1) if mainKeywordMatch and len(mainKeywordMatch.groups())>1 else ''
            #    mainKeyword = mainKeyword.translate({ord(x): '' for x in ['\'','~']}).strip()

            mainKeyword = keywords[0] if len(keywords) and not mainKeyword else mainKeyword
            mainKeyword = mainKeyword.upper()

            keywords = [k.upper().replace(',', '') for k in keywords if k.lower() != mainKeyword.lower()]
            #remove duplicatss if any within same record
            keywords = list(dict.fromkeys(keywords))
            #remove duplicates if any accorss records
            keywords = [k for k in keywords if k not in allRecordsKeywords]
            # keep track of keywords
            allRecordsKeywords.update(keywords)

            recordLines = recordLines[1:]

            syntaxesRaw = []
            matchedLines = []
            for rl in recordLines:
                syntaxRawMatch = re.findall(r'^syntax.+$', rl, re.IGNORECASE)
                syntaxesRaw += [re.sub('(?i)syntax\s*', 'Syntax:', s).replace('Syntax::','Syntax:') for s in syntaxRawMatch]
                if syntaxRawMatch:
                    matchedLines.append(rl)

            syntaxesRaw = [re.sub('Syntax:([^\s])', r'Syntax: \1', s) for s in syntaxesRaw]
            syntaxesRaw = [s.replace('Syntax: ', '').replace(',', '').strip() for s in syntaxesRaw if s.strip()]

            recordLines = [rl for rl in recordLines if rl not in matchedLines]

            seeAlso = []
            seeAlsoRaw = ''
            matchedLines = []
            for rl in reversed(recordLines):
                rl = rl.strip()
                if rl == '~' or rl == '':
                    pass
                elif re.search(r'^see[\s:]', rl, re.IGNORECASE):
                    seeAlsoRaw = rl + seeAlsoRaw
                    matchedLines.append(rl)
                    break
                elif len(rl) <= 25:
                    seeAlsoRaw += ' ' + rl
                    matchedLines.append(rl)
                else:
                    break
            seeAlsoRaw = seeAlsoRaw if re.search(r'^see[\s:]', seeAlsoRaw, re.IGNORECASE) else ''
            seeAlsoRaw = re.sub('(?i)^see(\s+also){0,1}\s*:*', '', seeAlsoRaw)
            multiKeywordsRaw = re.findall(r'\'[^\']+\'', seeAlsoRaw)
            for k in multiKeywordsRaw:
                seeAlso.append(k[1:-1])
                seeAlsoRaw = seeAlsoRaw.replace(k, '')
            if len(seeAlsoRaw) > 0:
                singleKeywordsRaw = [x.strip() for x in seeAlsoRaw.split(',') if x.strip() ]
            seeAlso += singleKeywordsRaw
            insensitive_help = re.compile(re.escape('help'), re.IGNORECASE)
            seeAlso = [insensitive_help.sub('',s.replace(',', '')).strip().upper() for s in seeAlso if s.lower() != 'help' and s.strip()]

            if seeAlsoRaw:
                recordLines = [rl for rl in recordLines if rl not in matchedLines]

            # check if first line contains the unneeded list of keywords 
            rl = recordLines[0].strip()
            rl = rl.replace('\'', '')
            if rl != '' and (rl == mainKeyword or rl in keywords or rl.isupper()):
                recordLines.pop(0)
            
            descriptionText = '\n'.join([x.strip() for x in recordLines if x.strip() != '~'])

            descriptionText = re.sub('\n\n([^\n])', r'\n\1', descriptionText)
            descriptionText = re.sub('\\\\br\s', r'\n\n', descriptionText)
            descriptionText = re.sub('\n{3,}', r'\n\n', descriptionText)
            descriptionText = descriptionText.strip()

            parsedRecord = {
                'restriction': restrictionType,
                'restriction_type': restrictionTypeSub,
                'keyword_main': mainKeyword,
                'keywords': ','.join(keywords) if keywords != '' else None,
                'syntax': ','.join(syntaxesRaw),
                'see_also': ','.join(seeAlso),
                'description': descriptionText,
                'raw': r
            }

            mainKeywordExists = False
            for i in range (0, len(parsedRecords)):
                mainKeywordExists = (parsedRecords[i]['keyword_main'] == mainKeyword)
                if mainKeywordExists:
                    break
            if mainKeywordExists:
                parsedRecords[i].update(parsedRecord)
            else:    
                parsedRecords.append(parsedRecord)

        return parsedRecords


class GameHelpFile(base_formats.TextFormat):
    TABLIB_MODULE = 'tablib.formats._game help file'
    CONTENT_TYPE = 'text/plain'

    def get_format(self):
         from tablib.formats import registry
         registry.register(self.get_title(), GameHelpFileFormat())
         return super().get_format()

    def get_title(self):
        key = self.TABLIB_MODULE.split('.')[-1].replace('_', '')
        return key
