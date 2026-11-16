#!/usr/bin/env python3
"""Deterministic standard-library renderer for The Door in the Sun."""
import math
import random
import struct
import sys
import zlib
from pathlib import Path

W = H = 1024
SEED = 73191


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def save_png(path, w, h, pixels):
    raw = b"".join(b"\0" + pixels[y*w*3:(y+1)*w*3] for y in range(h))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)


def downsample(src, size=300):
    out = bytearray(size * size * 3)
    for y in range(size):
        y0, y1 = y * H // size, (y + 1) * H // size
        for x in range(size):
            x0, x1 = x * W // size, (x + 1) * W // size
            n = (x1-x0)*(y1-y0)
            for c in range(3):
                total = 0
                for yy in range(y0, y1):
                    row = yy*W*3
                    total += sum(src[row + xx*3+c] for xx in range(x0, x1))
                out[(y*size+x)*3+c] = total//n
    return out


FONT = {
 'A':("01110","10001","10001","11111","10001","10001","10001"), 'B':("11110","10001","10001","11110","10001","10001","11110"),
 'C':("01111","10000","10000","10000","10000","10000","01111"), 'D':("11110","10001","10001","10001","10001","10001","11110"),
 'E':("11111","10000","10000","11110","10000","10000","11111"), 'F':("11111","10000","10000","11110","10000","10000","10000"),
 'G':("01111","10000","10000","10111","10001","10001","01111"), 'H':("10001","10001","10001","11111","10001","10001","10001"),
 'I':("11111","00100","00100","00100","00100","00100","11111"), 'J':("00111","00010","00010","00010","10010","10010","01100"),
 'L':("10000","10000","10000","10000","10000","10000","11111"), 'N':("10001","11001","11001","10101","10011","10011","10001"),
 'O':("01110","10001","10001","10001","10001","10001","01110"), 'P':("11110","10001","10001","11110","10000","10000","10000"),
 'R':("11110","10001","10001","11110","10100","10010","10001"), 'S':("01111","10000","10000","01110","00001","00001","11110"),
 'T':("11111","00100","00100","00100","00100","00100","00100"), 'U':("10001","10001","10001","10001","10001","10001","01110"),
 'Y':("10001","10001","01010","00100","00100","00100","00100"), ':':("00000","00100","00100","00000","00100","00100","00000"),
 '.':("00000","00000","00000","00000","00000","00110","00110"), '!':("00100","00100","00100","00100","00100","00000","00100"),
 ' ': ("00000",)*7,
}


def render(variant=5):
    rng = random.Random(SEED)
    img = bytearray(W*H*3)
    configs = {
        1: (512, 424, 250, 72, 1.00), 2: (565, 414, 270, 78, 1.00),
        3: (565, 414, 270, 78, 1.18), 4: (585, 412, 286, 82, 1.18),
        5: (585, 412, 286, 82, 1.12),
    }
    cx, cy, radius, text_y, contrast = configs.get(variant, configs[5])

    def blend(x, y, color, a):
        if 0 <= x < W and 0 <= y < H and a > 0:
            k=(y*W+x)*3; a=min(1.0,a)
            img[k]=min(255,int(img[k]*(1-a)+color[0]*a)); img[k+1]=min(255,int(img[k+1]*(1-a)+color[1]*a)); img[k+2]=min(255,int(img[k+2]*(1-a)+color[2]*a))

    def disk(xc,yc,r,color,opacity=1):
        rr=max(1,int(r+2))
        for y in range(max(0,int(yc)-rr),min(H,int(yc)+rr+1)):
            for x in range(max(0,int(xc)-rr),min(W,int(xc)+rr+1)):
                d=math.hypot(x+.5-xc,y+.5-yc); cov=max(0,min(1,r+.7-d))*opacity
                blend(x,y,color,cov)

    # Ink-black night with a faint blue-violet horizon and one warm, rising portal.
    for y in range(H):
        t=y/H
        base=(2+int(5*t), 3+int(4*t), 15+int(16*t))
        for x in range(W):
            q=((x-470)/720)**2+((y-460)/620)**2
            glow=max(0,1-math.sqrt(q))
            k=(y*W+x)*3
            img[k]=min(255,base[0]+int(13*glow)); img[k+1]=min(255,base[1]+int(4*glow)); img[k+2]=min(255,base[2]+int(38*glow))

    # Perspective streaks converge at the white-hot breach; varied color avoids a stock blast.
    for i in range(48):
        a=2*math.pi*i/48 + .025*math.sin(i*3)
        ca,sa=math.cos(a),math.sin(a)
        length=460 + rng.randrange(100,390)
        col=((255,65,118) if i%3==0 else (255,137,48) if i%3==1 else (51,220,255))
        width=2 if i%5 else 4
        for j in range(80, length, 3):
            xx=int(cx+ca*j + sa*j*.055); yy=int(cy+sa*j - ca*j*.055)
            fade=min(1,(j-80)/100)*max(.08,1-(j/length)**2)
            disk(xx,yy,width*(.7+j/length*.6),col,.12*fade*contrast)

    # Expanding shockwave arcs: offset slightly so the portal reads as a door opening.
    for rad,col,op,thick in ((radius+15,(255,56,154),.68,4),(radius+47,(255,137,50),.52,3),(radius+91,(55,211,255),.36,2)):
        for deg in range(0,360):
            a=math.radians(deg)
            disk(int(cx+rad*math.cos(a)),int(cy+rad*.79*math.sin(a)),thick,col,op)

    # Broad aureole and broken elliptical rim.
    for rad in range(radius+18, radius+4, -2):
        op=.018*(radius+18-rad+1)
        for deg in range(0,360,2):
            a=math.radians(deg); disk(int(cx+rad*math.cos(a)),int(cy+rad*.82*math.sin(a)),3,(255,82,136),op)
    for deg in range(0,360):
        a=math.radians(deg)
        # A deliberate gap at upper right makes the threshold feel torn open.
        if 300 < deg < 348: continue
        rad=radius + 8*math.sin(5*a)+5*math.sin(11*a)
        col=(255,100+int(90*(.5+.5*math.sin(7*a))),44)
        disk(int(cx+rad*math.cos(a)),int(cy+rad*.82*math.sin(a)),5,col,.95)

    # Portal interior: magenta edge -> orange plasma -> small, clean white center.
    for y in range(max(0,cy-radius),min(H,cy+radius)):
        for x in range(max(0,cx-radius),min(W,cx+radius)):
            dx=(x-cx)/radius; dy=(y-cy)/(radius*.82); d=math.hypot(dx,dy)
            if d < 1:
                hot=max(0,1-math.hypot((x-cx+20)/120,(y-cy-18)/104))
                if variant == 5:
                    rim=max(0,min(1,(d-.48)/.47))
                    col=(int(255-86*rim),int(67-50*rim),int(24+91*rim))
                    col=(min(255,col[0]+int(22*hot)),min(255,col[1]+int(110*hot)),min(255,col[2]+int(160*hot)))
                else:
                    edge=max(0,min(1,(1-d)*5))
                    col=(int(95+155*edge+5*hot),int(9+62*edge+230*hot),int(70+75*edge+255*hot))
                blend(x,y,col,.98)
    # Splitting fissures in the aperture, with white-gold branches.
    for points in [[(cx-28,cy-205),(cx-9,cy-116),(cx-48,cy-66),(cx-15,cy+8),(cx+5,cy+75)],
                   [(cx+70,cy-175),(cx+35,cy-108),(cx+83,cy-54),(cx+48,cy+16),(cx+62,cy+92)],
                   [(cx-9,cy-116),(cx+61,cy-151)],[(cx-48,cy-66),(cx-112,cy-33)],
                   [(cx+83,cy-54),(cx+146,cy-83)],[(cx-15,cy+8),(cx-80,cy+54)]]:
        for (x0,y0),(x1,y1) in zip(points,points[1:]):
            steps=max(abs(x1-x0),abs(y1-y0))
            for s in range(steps+1):
                t=s/max(1,steps); disk(round(x0+(x1-x0)*t),round(y0+(y1-y0)*t),2.5,(255,250,205),.9)

    # Core flare centered just above the midpoint, with a sharp white nucleus.
    if variant == 5:
        disk(cx,cy-18,132,(255,88,28),.30); disk(cx,cy-18,88,(255,190,82),.55); disk(cx,cy-18,51,(255,244,199),.94)
        disk(cx-5,cy-21,22,(255,255,255),1)
    else:
        disk(cx,cy-18,103,(255,110,66),.35); disk(cx,cy-18,59,(255,208,130),.62); disk(cx,cy-18,28,(255,255,237),.98)
        disk(cx-5,cy-21,11,(255,255,255),1)

    # Sparks and a few shards drift away from the threshold.
    for i in range(108):
        a=rng.random()*math.tau; rad=radius+rng.random()*285
        x=int(cx+math.cos(a)*rad); y=int(cy+math.sin(a)*rad*.82)
        s=rng.choice((1,1,2,3)); color=rng.choice(((255,195,112),(255,84,151),(71,224,255),(255,242,210)))
        disk(x,y,s,color,rng.uniform(.48,.98))
        if i%13==0:
            for q in range(5): disk(x+q*2,y-q,s*.55,color,.5)

    # Tilted cliff, drawn as a clean, dark wedge with a narrow cyan rim.
    for x in range(0,438):
        top=int(804 + .17*x + 11*math.sin(x/88))
        for y in range(max(0,top),H):
            shade=max(0,min(1,(y-top)/190)); blend(x,y,(4+int(4*shade),7+int(7*shade),17+int(17*shade)),1)
        for yy in range(top-1,top+2): blend(x,yy,(63,202,229),.68)
    # Fractured ledges catch the portal light.
    for x in range(50,420,47):
        y=int(804+.17*x+11*math.sin(x/88))
        disk(x,y,2,(255,125,83),.55)

    # Lone person on the edge, facing the opening: a restrained geometric silhouette.
    fx,fy=337,833
    if variant == 5:
        head, torso_top, torso_bottom, leg_len = 11, 34, 6, 36
    else:
        head, torso_top, torso_bottom, leg_len = 8, 24, 4, 26
    disk(fx,fy-torso_top-head+1,head,(2,4,12),1)
    # torso, coat, legs and one slightly raised arm
    for yy in range(fy-torso_top,fy+torso_bottom):
        half=(6 if yy<fy-7 else 11) if variant == 5 else (4 if yy<fy-5 else 8)
        for xx in range(fx-half,fx+half+1): blend(xx,yy,(2,4,12),1)
    for q in range(leg_len):
        blend(fx-5-q//12,fy+q,(2,4,12),1); blend(fx+5+q//14,fy+q,(2,4,12),1)
    for q in range(22 if variant == 5 else 17): blend(fx+5+q//7,fy-torso_top+7-q,(2,4,12),1)
    # Rim light traces one shoulder, preserving the silhouette at thumbnail scale.
    for q in range(24 if variant == 5 else 20): blend(fx+8,fy-torso_top+8+q,(91,205,229),.72 if variant == 5 else .55)

    # Small hand-built label, on a dark plaque with broad letterforms for 300px legibility.
    label="JUDGE: YOU JUST SAT UP."
    scale=4; charw=6*scale; total=len(label)*charw-scale; x0=(W-total)//2; y0=text_y
    # warm hairline + dark backing keeps label quiet and readable over the night
    for y in range(y0-10,y0+7*scale+10):
        for x in range(x0-16,x0+total+16): blend(x,y,(3,5,16),.9)
    for x in range(x0-15,x0+total+15): blend(x,y0-7,(52,190,221),.8)
    for n,ch in enumerate(label):
        glyph=FONT[ch]
        for gy,row in enumerate(glyph):
            for gx,v in enumerate(row):
                if v=='1':
                    for oy in range(scale):
                        for ox in range(scale): blend(x0+n*charw+gx*scale+ox,y0+gy*scale+oy,(250,248,239),1)

    return img


def main():
    variant=5; dest="/output/entry.png"
    args=sys.argv[1:]
    if args and args[0].isdigit(): variant=int(args.pop(0))
    if args: dest=args[0]
    image=render(variant)
    save_png(dest,W,H,image)
    if len(args)>1:
        save_png(args[1],300,300,downsample(image))


if __name__ == "__main__":
    main()
