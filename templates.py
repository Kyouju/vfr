#!/usr/bin/env python3.1

class AutoMKVChapters:
    class Template:
        def __init__(self):
            from random import randint
            self.uid = randint(10**4,10**6)
            self.num_editions = 1
            self.lang = ['eng']
            self.country = ['us']
            self.fps = '30'
            self.ofps = '24'
            self.qpf = '0'
            self.trims = None
            self.kframes = None

        def toxml(self,chapfile):

            chf = open(chapfile+'.xml','w',encoding='utf-8')
            head = '<?xml version="1.0" encoding="UTF-8"?>\n<!-- <!DOCTYPE Tags SYSTEM "matroskatags.dtd"> -->\n'
            chf.write(head+'<Chapters>\n')
            
            if self.num_editions > 1:
                tagf = open(chapfile+'tags.xml','w')
                tagf.write(head+'<Tags>\n')
            else:
                tagf = False

            for ed in self.editions:
                chf.write('\t<EditionEntry>\n')
                chf.write('\t\t<EditionFlagHidden>%d</EditionFlagHidden>\n' % ed.hidden)
                chf.write('\t\t<EditionFlagDefault>%d</EditionFlagDefault>\n' % ed.default)
                chf.write('\t\t<EditionFlagOrdered>%d</EditionFlagOrdered>\n' % ed.ordered)
                chf.write('\t\t<EditionUID>%d</EditionUID>\n' % ed.uid)
                
                if tagf:
                    tagf.write('\t<Tag>\n\t\t<Targets>\n')
                    tagf.write('\t\t\t<EditionUID>%d</EditionUID>\n' % ed.uid)
                    tagf.write('\t\t\t<TargetTypeValue>50</TargetTypeValue>\n\t\t</Targets>\n')
                    num_names = len(ed.name) if len(ed.name) < len(self.lang) else len(self.lang)
                    for i in range(num_names):
                        tagf.write('\t\t<Simple>\n\t\t\t<Name>TITLE</Name>\n')
                        tagf.write('\t\t\t<String>%s</String>\n' % (ed.name[i] if ed.name[i] != '' else ed.name[i-1]))
                        tagf.write('\t\t\t<TagLanguage>%s</TagLanguage>\n' % self.lang[i])
                        tagf.write('\t\t\t<DefaultLanguage>%d</DefaultLanguage>\n' % (1 if i == 0 else 0))
                        tagf.write('\t\t</Simple>\n')
                    tagf.write('\t</Tag>\n')

                for ch in ed.chapters:
                    chf.write('\t\t<ChapterAtom>\n')
                    num_names = len(ch.name) if len(ch.name) < len(self.lang) else len(self.lang)
                    for i in range(num_names):
                        chf.write('\t\t\t<ChapterDisplay>\n')
                        chf.write('\t\t\t\t<ChapterString>%s</ChapterString>\n' % (ch.name[i] if ch.name[i] != '' else ch.name[i-1]))
                        chf.write('\t\t\t\t<ChapterLanguage>%s</ChapterLanguage>\n' % self.lang[i])
                        chf.write('\t\t\t\t<ChapterCountry>%s</ChapterCountry>\n' % self.country[i] if i < len(self.country) else '')
                        chf.write('\t\t\t</ChapterDisplay>\n')
                    chf.write('\t\t\t<ChapterUID>%d</ChapterUID>\n' % ch.uid)
                    chf.write('\t\t\t<ChapterTimeStart>%s</ChapterTimeStart>\n' % ch.start)
                    chf.write('\t\t\t<ChapterTimeEnd>%s</ChapterTimeEnd>\n' % ch.end)
                    chf.write('\t\t\t<ChapterFlagHidden>%d</ChapterFlagHidden>\n' % ch.hidden if ch.hidden != 0 else '')
                    chf.write('\t\t\t<ChapterFlagEnabled>%d</ChapterFlagEnabled>\n' % ch.enabled if ch.enabled != 1 else '')
                    chf.write('\t\t\t<ChapterSegmentUID format="hex">%s</ChapterSegmentUID>\n' % ch.suid if ch.suid else '')
                    chf.write('\t\t</ChapterAtom>\n')
                
                chf.write('\t</EditionEntry>\n')

            chf.write('</Chapters>\n')

            if tagf:
                tagf.write('</Tags>\n')
                tagf.close()

            if self.qpf != '0' and self.kframes:
                from vfr import write_qpfile
                if self.qpf != '1':
                    qpfile = self.qpf
                else:
                    qpfile = chapfile+'.qpfile'
                write_qpfile(qpfile,self.kframes)

        def connect_with_vfr(self,avs):
            """
            Connects templates.py with vfr.py, enabling its use outside of vfr.py.
            
            Uses the same quirks as AMkvC but only for 24 and 30 fps.
            Ex: inputfps=30 is understood as being '30*1000/1001'
            
            """

            from vfr import parse_trims, fmt_time

            # compensate for amkvc's fps assumption
            if self.fps in ('24','30'):
                fps = '%s/1.001' % self.fps
            else:
                self.fps = str(fps)
            if self.ofps and self.ofps in ('24','30'):
                ofps = '%s/1.001' % self.ofps
            else:
                ofps = str(self.ofps)
            Trims2, Trims2ts = parse_trims(avs, fps, ofps)[2:4]
            Trims2ts = [(fmt_time(i[0]),fmt_time(i[1])) for i in Trims2ts]

            self.trims = Trims2ts
            self.kframes = Trims2

        class Edition:
            def __init__(self):
                self.default = 0
                self.name = 'Default'
                self.hidden = 0
                self.ordered = 0
                self.num_chapters = 1
                self.uid = 0

        class Chapter:
            def __init__(self):
                self.name = 'Chapter'
                self.chapter = False
                self.start = False
                self.end = False
                self.suid = False
                self.hidden = 0
                self.uid = 0
                self.enabled = 1

    def __init__(self, templatefile, output=None, avs=None, trims=None, kframes=None, uid=None):
        import configparser
        
        # Init config
        config = configparser.ConfigParser()
        template = open(templatefile,encoding='utf-8')

        # Read template
        config.readfp(template)
        template.close()
        
        # Template defaults
        self = self.Template()
        self.editions = []
        self.uid = uid if uid else self.uid

        for k, v in config.items('info'):
            if k == 'lang':
                self.lang = v.split(',')
            elif k == 'country':
                self.country = v.split(',')
            elif k == 'inputfps':
                self.fps = v
            elif k == 'outputfps':
                self.ofps = v
            elif k == 'createqpfile':
                self.qpf = v
            elif k == 'uid':
                self.uid = int(v)
            elif k == 'editions':
                self.num_editions = int(v)

        if avs:
            self.connect_with_vfr(avs)
        elif trims:
            self.trims = trims
            self.kframes = kframes
        else:
            self.trims = False

        for i in range(self.num_editions):
            from re import compile
            ed = self.Edition()
            ed.uid = self.uid * 100
            self.uid += 1
            cuid = ed.uid
            ed.num = i+1
            ed.chapters = []
            stuff = {}
            
            for k, v in config.items('edition%d' % ed.num):
                if k == 'default':
                    ed.default = int(v)
                elif k == 'name':
                    ed.name = v.split(',')
                elif k == 'ordered':
                    ed.ordered = int(v)
                elif k == 'hidden':
                    ed.hidden = int(v)
                elif k == 'chapters':
                    ed.num_chapters = int(v)
                    for i in range(ed.num_chapters):
                        stuff[i+1] = []
                elif k == 'uid':
                    ed.uid = int(v)
                else:
                    opt_re = compile('(\d+)(\w+)')
                    ret = opt_re.search(k)
                    if ret:
                        stuff[int(ret.group(1))].append((ret.group(2),v))

            for j in range(ed.num_chapters):
                ch = self.Chapter()
                cuid += 1
                ch.uid = cuid
                ch.num = j+1
                
                for k, v in stuff[j+1]:
                    if k == 'name':
                        ch.name = v.split(',')
                    elif k == 'chapter':
                        ch.chapter = int(v)
                    elif k == 'start':
                        ch.start = v
                    elif k == 'end':
                        ch.end = v
                    elif k == 'suid':
                        ch.suid = v
                    elif k == 'hidden':
                        ch.hidden = int(v)
                    elif k == 'enabled':
                        ch.enabled = int(v)

                if ch.chapter and not (ch.start and ch.end):
                    ch.start, ch.end = self.trims[ch.chapter-1] if self.trims else (ch.start, ch.end)
                elif ch.suid:
                    from os.path import isfile
                    from subprocess import check_output
                    
                    suid_re = compile('^\| \+ Segment UID: (.*)(?m)')
                    duration_re = compile('^\| \+ Duration: \d+\.\d*s \((\d+:\d+:\d+.\d+)\)(?m)')
                    suid = None
                    if isfile(ch.suid):
                        info = check_output(['mkvinfo','--output-charset','utf-8',ch.suid]).decode('utf-8')
                        ret = suid_re.search(info)
                        suid = ret.group(1).strip().replace('0x','').replace(' ','') if ret else 0
                    else:
                        from glob import glob
                        mkvfiles = glob('*.mkv')
                        for file in mkvfiles:
                            info = check_output(['mkvinfo','--output-charset','utf-8',file]).decode('utf-8')
                            ret = suid_re.search(info)
                            suid = ret.group(1).strip().replace('0x','').replace(' ','') if ret else 0
                            if suid == ch.suid.strip().replace('0x','').replace(' ',''):
                                break
                    if suid and not ch.start or ch.end:
                        ret = duration_re.search(info)
                        if ret:
                            ch.suid = suid
                            ch.start = '00:00:00.000' if ch.start == False else ch.start
                            ch.end = ret.group(1) if ch.end == False else ch.end
                    else:
                        ch.suid = False
                        ch.start = '00:00:00.000'
                        ch.end = '00:00:00.000'
                        ch.enabled = 0
                        
                ed.chapters.append(ch)
            self.editions.append(ed)
        if output:
            self.toxml(output)


def main(args):

    template = args[0]
    output = args[1]
    avs = args[2] if len(args) == 3 else None

    chaps = AutoMKVChapters(template,output,avs)

if __name__ == '__main__':
    from sys import argv, exit
    if len(argv) > 1:
        main(argv[1:])
    else:
        exit("templates.py <template file> <output filenames w/o extension> [<avisynth file>]")