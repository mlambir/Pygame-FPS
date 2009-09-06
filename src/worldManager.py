import pygame
from pygame.locals import *
import math
    
texWidth = 64
texHeight = 64
class WorldManager(object):

    def __init__(self,worldMap,sprite_positions,x,y,dirx,diry,planex,planey):
        self.sprites = [  
              load_image(pygame.image.load("pics/items/barrel.png").convert(), False, colorKey = (0,0,0)),
              load_image(pygame.image.load("pics/items/pillar.png").convert(), False, colorKey = (0,0,0)),
              load_image(pygame.image.load("pics/items/greenlight.png").convert(), False, colorKey = (0,0,0)),
        ]
        
        self.background = None
        self.images = [  
              load_image(pygame.image.load("pics/walls/eagle.png").convert(), False),
              load_image(pygame.image.load("pics/walls/redbrick.png").convert(), False),
              load_image(pygame.image.load("pics/walls/purplestone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/greystone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/bluestone.png").convert(), False),
              load_image(pygame.image.load("pics/walls/mossy.png").convert(), False),
              load_image(pygame.image.load("pics/walls/wood.png").convert(), False),
              load_image(pygame.image.load("pics/walls/colorstone.png").convert(), False),
    
              load_image(pygame.image.load("pics/walls/eagle.png").convert(), True),
              load_image(pygame.image.load("pics/walls/redbrick.png").convert(), True),
              load_image(pygame.image.load("pics/walls/purplestone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/greystone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/bluestone.png").convert(), True),
              load_image(pygame.image.load("pics/walls/mossy.png").convert(), True),
              load_image(pygame.image.load("pics/walls/wood.png").convert(), True),
              load_image(pygame.image.load("pics/walls/colorstone.png").convert(), True),
              ]
        self.camera = Camera(x,y,dirx,diry,planex,planey)
        self.worldMap = worldMap
        self.sprite_positions = sprite_positions
    def draw(self, surface):
        w = surface.get_width()
        h = surface.get_height()
        #draw background
        if self.background is None:
            self.background = pygame.transform.scale(pygame.image.load("pics/background.png").convert(), (w,h))
        surface.blit(self.background, (0,0))
        zBuffer = []
        for x in range(w):
            #calculate ray position and direction 
            cameraX = float(2 * x / float(w) - 1) #x-coordinate in camera space
            rayPosX = self.camera.x
            rayPosY = self.camera.y
            rayDirX = self.camera.dirx + self.camera.planex * cameraX
            rayDirY = self.camera.diry + self.camera.planey * cameraX
            #which box of the map we're in  
            mapX = int(rayPosX)
            mapY = int(rayPosY)
       
            #length of ray from current position to next x or y-side
            sideDistX = 0.
            sideDistY = 0.
       
            #length of ray from one x or y-side to next x or y-side
            deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / (rayDirX * rayDirX))
            if rayDirY == 0: rayDirY = 0.00001
            deltaDistY = math.sqrt(1 + (rayDirX * rayDirX) / (rayDirY * rayDirY))
            perpWallDist = 0.
       
            #what direction to step in x or y-direction (either +1 or -1)
            stepX = 0
            stepY = 0

            hit = 0 #was there a wall hit?
            side = 0 # was a NS or a EW wall hit?
            
            # calculate step and initial sideDist
            if rayDirX < 0:
                stepX = - 1
                sideDistX = (rayPosX - mapX) * deltaDistX
            else:
                stepX = 1
                sideDistX = (mapX + 1.0 - rayPosX) * deltaDistX
                
            if rayDirY < 0:
                stepY = - 1
                sideDistY = (rayPosY - mapY) * deltaDistY
            else:
                stepY = 1
                sideDistY = (mapY + 1.0 - rayPosY) * deltaDistY
                
            # perform DDA
            while hit == 0:
                # jump to next map square, OR in x - direction, OR in y - direction
                if sideDistX < sideDistY:
        
                    sideDistX += deltaDistX
                    mapX += stepX
                    side = 0
                else:
                    sideDistY += deltaDistY
                    mapY += stepY
                    side = 1

                # Check if ray has hit a wall
                if (self.worldMap[mapX][mapY] > 0): 
                    hit = 1
            # Calculate distance projected on camera direction (oblique distance will give fisheye effect !)
            if (side == 0):
                #perpWallDist = fabs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX)
                perpWallDist = (abs((mapX - rayPosX + (1 - stepX) / 2) / rayDirX))
            else:
                perpWallDist = (abs((mapY - rayPosY + (1 - stepY) / 2) / rayDirY))
      
            # Calculate height of line to draw on surface
            if perpWallDist == 0:perpWallDist = 0.000001
            lineHeight = abs(int(h / perpWallDist))
       
            # calculate lowest and highest pixel to fill in current stripe
            drawStart = - lineHeight / 2 + h / 2
            drawEnd = lineHeight / 2 + h / 2
        
            #texturing calculations
            texNum = self.worldMap[mapX][mapY] - 1; #1 subtracted from it so that texture 0 can be used!
           
            #calculate value of wallX
            wallX = 0 #where exactly the wall was hit
            if (side == 1):
                wallX = rayPosX + ((mapY - rayPosY + (1 - stepY) / 2) / rayDirY) * rayDirX
            else:
                wallX = rayPosY + ((mapX - rayPosX + (1 - stepX) / 2) / rayDirX) * rayDirY;
            wallX -= math.floor((wallX));
           
            #x coordinate on the texture
            texX = int(wallX * float(texWidth))
            if(side == 0 and rayDirX > 0): 
                texX = texWidth - texX - 1;
            if(side == 1 and rayDirY < 0): 
                texX = texWidth - texX - 1;

            if(side == 1):
                texNum +=8
            if lineHeight > 10000:
                lineHeight=10000
                drawStart = -10000 /2 + h/2
            surface.blit(pygame.transform.scale(self.images[texNum][texX], (1, lineHeight)), (x, drawStart))
            zBuffer.append(perpWallDist)

        #function to sort sprites
        def sprite_compare(s1, s2):
            import math
            s1Dist = math.sqrt((s1[0] -self.camera.x) ** 2 + (s1[1] -self.camera.y) ** 2)
            s2Dist = math.sqrt((s2[0] -self.camera.x) ** 2 + (s2[1] -self.camera.y) ** 2)  
            if s1Dist>s2Dist:
                return -1
            elif s1Dist==s2Dist:
                return 0
            else:
                return 1
        #draw sprites
        
        self.sprite_positions.sort(sprite_compare)
        for sprite in self.sprite_positions:
            #translate sprite position to relative to camera
            spriteX = sprite[0] - self.camera.x;
            spriteY = sprite[1] - self.camera.y;
             
            #transform sprite with the inverse camera matrix
            # [ self.camera.planex   self.camera.dirx ] -1                                       [ self.camera.diry      -self.camera.dirx ]
            # [               ]       =  1/(self.camera.planex*self.camera.diry-self.camera.dirx*self.camera.planey) *   [                 ]
            # [ self.camera.planey   self.camera.diry ]                                          [ -self.camera.planey  self.camera.planex ]
          
            invDet = 1.0 / (self.camera.planex * self.camera.diry - self.camera.dirx * self.camera.planey) #required for correct matrix multiplication
          
            transformX = invDet * (self.camera.diry * spriteX - self.camera.dirx * spriteY)
            transformY = invDet * (-self.camera.planey * spriteX + self.camera.planex * spriteY) #this is actually the depth inside the surface, that what Z is in 3D       
                
            spritesurfaceX = int((w / 2) * (1 + transformX / transformY))
          
            #calculate height of the sprite on surface
            spriteHeight = abs(int(h / (transformY))) #using "transformY" instead of the real distance prevents fisheye
            #calculate lowest and highest pixel to fill in current stripe
            drawStartY = -spriteHeight / 2 + h / 2
            drawEndY = spriteHeight / 2 + h / 2
          
            #calculate width of the sprite
            spriteWidth = abs( int (h / (transformY)))
            drawStartX = -spriteWidth / 2 + spritesurfaceX
            drawEndX = spriteWidth / 2 + spritesurfaceX
            
            if spriteHeight < 1000:
                for stripe in range(drawStartX, drawEndX):
                    texX = int(256 * (stripe - (-spriteWidth / 2 + spritesurfaceX)) * texWidth / spriteWidth) / 256
                    #the conditions in the if are:
                    ##1) it's in front of camera plane so you don't see things behind you
                    ##2) it's on the surface (left)
                    ##3) it's on the surface (right)
                    ##4) ZBuffer, with perpendicular distance
                    if(transformY > 0 and stripe > 0 and stripe < w and transformY < zBuffer[stripe]):
                        surface.blit(pygame.transform.scale(self.sprites[sprite[2]][texX], (1, spriteHeight)), (stripe, drawStartY))
    

class Camera(object):
    def __init__(self,x,y,dirx,diry,planex,planey):
        self.x = float(x)
        self.y = float(y)
        self.dirx = float(dirx)
        self.diry = float(diry)
        self.planex = float(planex)
        self.planey = float(planey)
        

def load_image(image, darken, colorKey = None):
    ret = []
    if colorKey is not None:
        image.set_colorkey(colorKey)
    if darken:
        image.set_alpha(127)
    for i in range(image.get_width()):
        s = pygame.Surface((1, image.get_height())).convert()
        #s.fill((0,0,0))
        s.blit(image, (- i, 0))
        if colorKey is not None:
            s.set_colorkey(colorKey)
        ret.append(s)
    return ret