from PIL import Image
img = Image.open('identities.png')
w, h = img.size
area = (84, 293, w - 117, h - 324)
new_img = img.crop(area)
nw, nh = new_img.size
nw = nw // 5
nh = nh // 2
names = ['liberal', 'hitler', 'fascist']
for i in range(2, 5):
    x1 = nw * i
    x2 = x1 + nw
    y1 = 0
    y2 = nh
    img = new_img.crop((x1, y1, x2, y2))
    img.save(names[i - 2] + '.png')