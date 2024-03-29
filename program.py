"""
DTMF DECODER
this code contains simple way to decode dtmf signals in rate 8000
"""
import numpy as np
from pyaudio import PyAudio, paInt16

RATE = 8000
DURATION = 0.25
CHUNK_SIZE = 1024
KEYS = [['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']]


def record_audio():
    """
    this function record audio and convert it to numpy array
    """
    recorder = PyAudio()
    stream = recorder.open(format=paInt16,
                           channels=1,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK_SIZE)

    frames = []
    for _ in range(int(RATE / CHUNK_SIZE * DURATION) + 1):
        data = stream.read(CHUNK_SIZE)
        frames.append(np.fromstring(data, dtype=np.int16))

    numpydata = np.hstack(frames)
    stream.stop_stream()
    stream.close()
    recorder.terminate()
    return numpydata


def frq_index_finder(h_frq, l_frq):
    """
    this function return output key by finding indexes of DTMF table by frequency comparision
    :param h_frq: input high frequency
    :param l_frq: input low frequency
    :return: output key as String
    """
    row = -1
    column = -1
    h_frq = int(h_frq)
    l_frq = int(l_frq)
    
    # compare low frequency to find index of row
    if 658 < l_frq < 733:
        row = 0
    elif 733 < l_frq < 811:
        row = 1
    elif 811 < l_frq < 896:
        row = 2
    elif 896 < l_frq < 985:
        row = 3

    # compare high frequency to find index of column
    if 1145 < h_frq < 1273:
        column = 0
    elif 1273 < h_frq < 1406:
        column = 1
    elif 1406 < h_frq < 1555:
        column = 2
    elif 1555 < h_frq < 1711:
        column = 3

    return key_finder_by_indexes(row, column)


def key_finder_by_indexes(row, column):
    """
    select pressed key by input row and column
    """
    if (row < 4 and row > -1 and column < 4 and column > -1):
        return KEYS[row][column]
    # return 'Unknown Key!'
    return None


def max_frq(y, frq):
    """
    find maximum frequency in sample
    :param y: input sample
    :param frq: input frequency
    :return: maximum element
    """
    y = np.absolute(y)
    index = np.where(y == np.amax(y))
    return frq[index]


def dtmf_decoder(sample):
    """
    decode input sample by fft and frequency selection
    """
    n = sample.shape[0]
    k = np.arange(n)
    t = n / RATE
    frq = k / t
    frq = frq[range(int(n / 2))]
    y = np.fft.fft(sample) / n
    y = y[range(int(n / 2))]
    # find high frequency
    h_frq = max_frq(y, frq)
    index = 0
    # find low frequency
    for i in range(0, len(frq)):
        if frq[i] < 1145:
            index = i
    l_frq = max_frq(y[:index], frq[:index])
    return frq_index_finder(h_frq, l_frq)


def main():
    print('Enter key:...')
    while True:
        sample = record_audio()
        output = dtmf_decoder(sample)
        if output != None:
            print('Your entered key was ', output)
            print('Enter another key:...')


if __name__ == '__main__':
    main()
