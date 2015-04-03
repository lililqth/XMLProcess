# coding=utf-8
import sys
f = open('test.vhd', 'r')
fAfter = open('afterProcess.vhd', 'w')
lines = f.readlines()


def getLine(line):
    i = line.find('--')
    return line[:i] + line[i + 2:]

if __name__ == "__main__":
    start = False
    replace = False
    for line in lines:
        if "%% start" in line:
            start = True
            continue
        if start == True and not line.strip()[0:2] == "--":
            start = False
            replace = True
        if replace == True and "%% end" in line:
            replace = False
            continue

        if start == True:
            fAfter.writelines(getLine(line))
        elif replace == True:
            continue
        else:
            fAfter.writelines(line)
    fAfter.close()
    f.close()
