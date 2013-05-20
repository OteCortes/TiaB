#-*- coding: utf-8 -*-
from PIL import Image
import os.path
import hashlib
import binascii


class Tiab:
    def __init__(self, imagepath, passkey, outpath=None):
        self.imagepath = imagepath
        self.outpath = outpath
        self.passkey = self.__hasherize(passkey)
        self.image = self.__loadImage()
        #self.channelR,self.channelG,self.channelB=self.__colorList()
        self.origPixelList = self.__colorList()
        self.finalPixelList = []
        self.pixels = len(self.origPixelList)
        self.textlengh=0

    #Load the image data from the file
    def __loadImage(self):
        if(os.path.exists(self.imagepath)):
            try:
                return(Image.open(self.imagepath))
            except Exception as e:
                print("Error opening image %s \n %s"%(self.imagepath,e))

    #Save the coded image
    def __saveImage(self):
        if not self.outpath:
            self.outpath=os.path.dirname(self.imagepath) + "/coded_" + os.path.basename(self.imagepath)
        
        if (not os.path.exists(self.outpath)):
            try:
                self.image.putdata(self.finalPixelList)
                self.image.save(self.outpath)
            except Exception as e:
                print("Error saving file\n %s"%e)
        else:
            print("Output file already exists....aborting")

    #Prepare the hash of the key
    def __hasherize(self,key):
        complete = hashlib.sha512(key.encode("utf-8")).hexdigest()

        return(self.__text2bitlist(complete))

    #prepare the pixel data list
    def __colorList(self):
        #Image to RGBA to use the 4 channels
        if self.image.mode != ( 'RGBA'):
            self.image = self.image.convert('RGBA')

        #get the pixel information.
        return(list(self.image.getdata()))


    #Convert text list to bit list to XOR
    def __text2bitlist(self,text):
        encoded=text.encode("utf-8")
        out=[]

        #Ascii to Hex, ext to Int, int to Binary String, bit to true/false
        binary=bin(int(binascii.hexlify(encoded), 16))[2:]
        for bit in binary:
            if bit=='0':
                out.append(False)
            elif bit=='1':
                out.append(True)
        return(out)

    #the bitlist format to text
    def __bitlist2text(self,binary):
        bitstring = []

        for bit in binary:
            if bit:
                bitstring.append('1')
            else:
                bitstring.append('0')
        binstring="".join(bitstring)
        hexa=int(binstring,2)
        hexa='%x'%hexa
        
       
        return(binascii.unhexlify(hexa.encode('ascii')).decode('utf-8'))
 

    ## Get the text size coded in the image or add it.
    def __codeTextSize(self,add=False):
        out=[]
        toadd=list(bin(self.textlengh)[2:].zfill(16))
        
        for x in range(0,16):
            if add:
                tmp=list(bin(self.origPixelList[x][0]))
                tmp[-1]=toadd[x]
                self.finalPixelList.append(((int("".join(tmp),2),self.origPixelList[x][1],self.origPixelList[x][2],self.origPixelList[x][3])))
                out.append(bin(self.finalPixelList[x][0])[-1])
            else:
                out.append(bin(self.origPixelList[x][0])[-1])

        return(int("".join(out),2))

    ##Mod the required pixels to add the text
    def __codeMsg(self,msg=None):
        if( (msg != None) and (len(msg)> self.pixels-16)):
            raise Exception("Image without enought pixels to hide the text")

        out=[]
        for x in range(16, self.textlengh+16):
            if msg:
                tmp=list(bin(self.origPixelList[x][0]))
                tmp[-1]='1' if msg[x-16] else '0'
                self.finalPixelList.append(((int("".join(tmp),2),self.origPixelList[x][1],self.origPixelList[x][2],self.origPixelList[x][3])))
                out.append(msg[x-16])
            else:
                out.append(True if bin(self.origPixelList[x][0])[-1]=='1' else False)

        #if msg added to the image, complete the final image with the original data.
        if msg:
            for pix in range(self.textlengh+17, self.pixels):
                self.finalPixelList.append(self.origPixelList[pix])
       
        return(out)
    
    #cipher with xor key to add little security to the Steganography
    def __cipher(self,data):
        #XOR with the hash in cicle
        for pos in range(0,self.textlengh-1):
            if pos < len(self.passkey):
                hashcursor=pos
            else:
                hashcursor= pos - len(self.passkey)

            data[pos] = data[pos]^self.passkey[hashcursor]

        return(data)

    #encode the text in the image
    def encode(self,text):
        data=self.__text2bitlist(text)
        self.textlengh=len(data)
        print(self.textlengh)
        self.__codeTextSize(add=True)

        #cipher a little the data
        data = self.__cipher(data)

        # Adding encoded data to image info
        self.__codeMsg(data)

        #Saving new coded image.
        self.__saveImage()
        print("Message coded in %s"%self.outpath)
     

    def decode(self):
        #Get the size to decode
        self.textlengh = self.__codeTextSize()
        #get the data to decode
        data=self.__codeMsg()
       
        try:
            #Try to decode
            data=self.__cipher(data)

            return(self.__bitlist2text(data))
        except Exception as e:
            print("Error in the decode. Check that 'imagefile' is a encoded image")


if __name__=='__main__':
    from Tiab import Tiab
    import argparse
    import sys
    
    #Prepare the argparse
    parser = argparse.ArgumentParser(description='Text in a Bottle. Steganography messages in imagefiles')
    parser.add_argument('passphrase',help='Password to encode or decode a image')
    parser.add_argument('imagefile',help='Path to the image used as base to encode or to decode')
    parser.add_argument('--out',help='Path to the output image for encode data in "imagefile". EXTENSION MUST BE THE SAME AS ORIGINAL "imagefile" ')
    parser.add_argument('--msg',help='Text to encode in the image')
    try:
        args = vars(parser.parse_args())
    except:
        parser.print_help()
        sys.exit(1)
    
    if (args['out']):
        tiab = Tiab(args['imagefile'],args['passphrase'],args['out'])
        tiab.encode(args['msg'])

    else:
        tiab = Tiab(args['imagefile'],args['passphrase'])
        print(tiab.decode())

