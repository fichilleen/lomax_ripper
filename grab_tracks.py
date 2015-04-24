import re
import sys

from urllib2 import urlopen

import BeautifulSoup
import eyed3

# This is for a commandline option I haven't bothered with yet
FORCE_ARTIST = False

# There are super lazy, but they work, because they're being used in a
# really narrow context without much text
mp3_pattern = re.compile('http.*?mp3')

f = sys.argv[1]
f_txt = None

if f.startswith('http'):
    f_txt = urlopen(f).read()
else:
    with open(f) as f_in:
            f_txt = f_in.read()

soup = BeautifulSoup.BeautifulSoup(f_txt)

def artist_transform(artist):
    ''' Change "Surname, Forname" format to "Forname Surname" '''
    if artist == 'Miller, Jimmy (Ewan MacColl)':
        # Special case, because he changed his name
        return u'Ewan MacColl'
    artist = artist.replace(',','').split(' ')
    return ' '.join((artist[1], artist[0]))



# TODO: We might want the year tag, but I'm too lazy and drunk to parse
# it now
def per_track(tds):
    title, mp3_url, artist = tds
    fn = '%s - %s.mp3' % (artist, title)
    with open(fn, 'wb') as mp3out:
        mp3out.write(urlopen(mp3_url).read())
    mp3 = eyed3.load(fn)
    mp3.tag.artist = artist
    mp3.tag.title = title
    mp3.tag.save()



# TRs are in groups of five.
# First one contains Title, Link, NameOfRecording
# Second one contains genre-like stuff and Artist
# Third one artist link/more genre-ish stuff
# Fifth one has artist, but we have to do some ugly parsing

parent_t = soup.find('table', 'displayTagTable').find('tbody')
td_group = []

for i, track in enumerate(parent_t.findChildren('tr')):
    if i % 5 == 0:
        if td_group:
            per_track(td_group)
        td_group = []

        track = track.findChildren()
        # Convert to str from unicode
        title = track[2].getText()
        mp3 = mp3_pattern.findall(str(track))[0]
        td_group.extend((title, mp3))

    elif i % 5 == 3:
        # Artist
        if FORCE_ARTIST:
            td_group.append(FORCE_ARTIST)
        else:
            artist = artist_transform(track.getText().split('[')[1][:-1])
            td_group.append(artist)

per_track(td_group)



