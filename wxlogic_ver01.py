import wx 
from wxui import MyFrame1 
import cv2
import threading
import time
import numpy as np
import os
import pickle
import copy
class Stage:
    def __init__(self, folder):
        self.path = os.path.join(folder,'stage.txt')
        self.append('starting')
    def append(self, text):
        with open(self.path,'a') as f:
            f.write(text+'\n')
    def lastest(self):
        with open(self.path,'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
        if last_line == 'starting':
            try:
                last_line = lines[-2]
            except:
                pass
        if last_line == 'starting': 
            last_line = 0
        return int(last_line)
class MyTracker():
    def __init__(self, cvimg, point, tracker_size=10):
        offset = tracker_size
        # roi = (left, top, width, height)
        self.center = point
        cx, cy = point[0], point[1]
        self.roi = cx-offset/2, cy-offset/2, offset, offset
        self.tracker = cv2.TrackerCSRT_create()
        self.tracker.init(cvimg, self.roi)

    def update(self, cvimg):
        success, self.roi = self.tracker.update(cvimg)
        left, top, width, height = self.roi
        self.center = left+width/2, top+height/2

class myframe(MyFrame1):
    def __init__(self, parent, app):
        MyFrame1.__init__(self, parent)
        app.Bind( wx.EVT_KEY_DOWN, self.on_key )
        self.saving_img_swap = False
        self.finish_setimg_temp = False
        self.init_cam = False
        self.currentpath = os.path.dirname(__file__)
        self.init_tracker_ = False
        self.init_open_imgfolder = False
        wx.Log.EnableLogging(False)
        self.color_hand = [wx.GREEN, wx.Colour(125, 60, 152), wx.GREEN, wx.BLUE,wx.BLUE]
        self.links = [[0,1] ,[0,3] ,[0,5] ,[0,7] ,[0,9], [1,2], [3,4], [5,6], [7,8], [9,10]]
        self.roi_show_ = False
        self.keypoint_show_ = True
        self.link_show_ = True
        self.left_swap = False
        self.move_point = False
        self.hand_mode = 11
        self.covered_point = [False for i in range(self.hand_mode)]
        self.keypoint_size = 3
        self.tracking_roi_size = 50
        self.checking_mode = False
        self.open_rm_bg_mode = False
        self.color_picker = []
        self.color_thres = []
        self.bg_color = (0,255,0)
        self.point_color = (0,0,255)
        self.mask = []
        self.set_mask_thres = False
        self.dist = 0
        self.a = 0
        self.off_tracker_mode = False


    def save_mp4( self, event ):
        event.Skip()

    def exit_program( self, event ):
        self.stop_cam = True
        self.cap_release(event)

    def opencam( self, event ):
        self.startcap()
        self.log('croped image from camera (1280,720)=>(720,720)')
        self.create_thread(self.show_img)
    def create_thread(self, target):
        self.thread = threading.Thread(target=target)
        #thread.daemon = True
        self.thread.start()
        
    def startcap(self):
        self.log('init video capture...')
        self.cap_ = cv2.VideoCapture(0)
        self.log('set video size to (1280, 720) ...')
        self.cap_.set(3, 1280)
        self.cap_.set(4, 720)
        
        
    def log(self, text):
        self.m_statusBar1.SetStatusText(text)
    def init_sav_vid(self):
        self.init_cam = True
        self.stop_cam = False
        self.imi = 0
        self.vid_saving = False
        self.take_video_on = False
        self.cnt = 'init'
        self.vid_saving_end = False
  
    def show_img(self):
        self.init_sav_vid()
        cnt = 'init'
        swap3 = self.vid_saving_end
        while not self.stop_cam:
            if swap3 != self.vid_saving_end:
                swap3 = self.vid_saving_end
                cnt = 'init'
                
            _, frame = self.cap_.read()
            w, h = 720, 720
            x, y = 1280/2-w/2, 720/2-h/2
            x, y, w, h = int(x), int(y), int(w), int(h)
            frame = frame[y:y+h, x:x+w]
            frame = cv2.flip(frame, 1)
            if self.take_video_on:
                if cnt == 'init':
                    t0 = time.time()
                    cnt = 3
                elif time.time()-t0 > 1 and cnt > 0:
                    t0 = time.time()
                    cnt -= 1
                elif cnt < 1:
                    self.take_video_on = False
                    self.vid_saving = True
            # if self.vid_saving:
            #     wx.CallAfter(self.after_show_img, 2, frame=frame)
            
                font = cv2.FONT_HERSHEY_SIMPLEX 
                org = int(720/2), int(720/2)
                fontScale = 3
                color = (255,0,255)
                thickness = 5
                frame = cv2.putText(frame, str(cnt), org, font,  
                        fontScale, color, thickness, cv2.LINE_AA)

            # write to save
            if self.vid_saving:
                swap2 = self.saving_img_swap
                wx.CallAfter(self.saving_img, frame)
                while self.saving_img_swap == swap2:
                    time.sleep(0.01)
        
            # resize and write to show
            frame = self.resize_cv2(frame, (500-2)/720)
            dir_temp = os.path.join(os.path.dirname(__file__)
                    ,'cv2_temp.bmp')
            swap = self.finish_setimg_temp

            # put on showing img
            if self.vid_saving:
                font = cv2.FONT_HERSHEY_SIMPLEX 
                org = 15,29
                fontScale = 0.7
                color = (255,255,0)
                thickness = 1
                frame = cv2.putText(frame, 'press space to stop recording..', org, font,  
                        fontScale, color, thickness, cv2.LINE_AA)
            if self.take_video_on:
                font = cv2.FONT_HERSHEY_SIMPLEX 
                org = 15,29
                fontScale = 1
                color = (255,10,255)
                thickness = 2
                frame = cv2.putText(frame, 'record in', org, font,  
                        fontScale, color, thickness, cv2.LINE_AA)

            if not self.take_video_on and not self.vid_saving:      
                font = cv2.FONT_HERSHEY_SIMPLEX 
                org = 15,29
                fontScale = 0.7
                color = (0,255,0)
                thickness = 1
                frame = cv2.putText(frame, 'press space to record', org, font,  
                        fontScale, color, thickness, cv2.LINE_AA)

            cv2.imwrite(dir_temp, frame)
            wx.CallAfter(self.add_static_img, dir_temp)
            
            while self.finish_setimg_temp == swap :
                time.sleep(0.01)
     
    def saving_img(self, frame):
        self.log('start saving...')
        self.imi += 1
        dir_imi = 'video_temp/'+str(self.fol).zfill(2)+'/'+str(self.imi).zfill(10)+'.bmp'
        frame = cv2.flip(frame, 1)
        cv2.imwrite(dir_imi,frame)
        self.log('saved %s'%dir_imi)
        self.saving_img_swap = not self.saving_img_swap
        self.vid_saving_end = True

    def resize_cv2(self, img, scale):
        scale_percent = scale*100
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        return resized
    def add_static_img(self, frame_location):
        if not self.stop_cam:
            wximg = wx.Bitmap(frame_location, wx.BITMAP_TYPE_ANY)
            self.m_bitmap5.SetBitmap(wximg)
            self.m_mgr.Update()
            self.finish_setimg_temp = not self.finish_setimg_temp

    def take_video( self, event ):
        if self.init_cam:
            self.mkfolder('video_temp')
            stage = Stage('video_temp')
            self.fol = stage.lastest() + 1
            stage.append(str(self.fol))
            self.mkfolder('video_temp/'+str(self.fol).zfill(2))
            self.take_video_on = True
            self.log('count down to take image...')
        else:
            wx.MessageBox('You have to init camera first.', 'Cannot record !',wx.OK )
    def stop_recording(self, event):
        if self.init_cam and self.vid_saving:
            self.init_sav_vid()
            self.log('remanage (.bmp) image file')

            # renew image due to some bugs of Thread.
            dir_temp = os.path.join('video_temp',str(self.fol).zfill(2))
            for _,_,fname in os.walk(dir_temp):
                pass 
            
            # remove 1, 2, 3, 4
            # rename 2->1, 4->2, 6->3
            for i in range(int(len(fname)/2)):
                newi = (i+1)*2
                oldi = newi - 1
                ci = i+1

                name_newi = str(newi).zfill(10)+'.bmp'
                dir_name_newi = os.path.join(dir_temp, name_newi)
                
                name_oldi = str(oldi).zfill(10)+'.bmp'
                dir_name_oldi = os.path.join(dir_temp, name_oldi)

                name_ci = str(ci).zfill(10)+'.bmp'
                dir_name_ci = os.path.join(dir_temp, name_ci)
                
                os.remove(dir_name_oldi)
                os.rename(dir_name_newi, dir_name_ci)
            try: 
                i = len(fname)
                namei = str(i).zfill(10)+'.bmp'
                dir_namei = os.path.join(dir_temp, namei)
                os.remove(dir_namei)
            except :pass
           
            # open current folder
            self.open_imgfolder_(event)
            self.log('done %d images in %s'%(int(len(fname)/2),dir_temp))

        else: 
            wx.MessageBox('There are no recording videos.', 'Cannot stop !',wx.OK )
    def mkfolder(self, name):
        if name not in os.listdir():
            os.mkdir(name)
            self.log('make___ (%s) ___folder'%name)
        else:
            self.log('found___ (%s) ___before make'%name)

    def open_imgfolder(self, event):
        self.checking_mode = False
        self.init_open_imgfolder = True
        fdir = ""  

        try:
            dir_temp = os.path.join(self.currentpath, 'video_temp')
            dlg = wx.DirDialog(self, defaultPath = dir_temp)
        except:        
            dlg = wx.DirDialog(self, defaultPath = self.currentpath)
        
        if dlg.ShowModal() == wx.ID_OK:
            fdir = dlg.GetPath()
            dlg.SetPath(fdir)
        dlg.Destroy()

        self.img_folder = fdir
        self.imi = 351 # <============== #################### config ###############################
        try:
            self.cap_.release()
        except :pass
        self.stop_cam = True # stop showing camera
        self.show_imi(self.imi)
        self.init_tracker(event)
     
    def open_imgfolder_(self, event):
        self.stop_cam = True # stop showing camera
        self.init_open_imgfolder = True
        fdir = os.path.join('video_temp',str(self.fol).zfill(2))  
        self.img_folder = fdir
        self.imi = 1
        try:
            self.cap_.release()
        except :pass

        self.show_imi(1)
        self.init_tracker(event)

    def show_imi(self, i):
        self.imi_path = os.path.join(self.img_folder
                    , str(i).zfill(10)+'.bmp')
        try:
            wximg = wx.Bitmap(self.imi_path, wx.BITMAP_TYPE_ANY)
            self.real_im = cv2.imread(self.imi_path)
        except:
            self.log('cannot read %s'%self.imi_path)
        width = wximg.GetWidth()
        self.real_im_width = width
        if width==0: self.log('width=0 check .bmp file')
        assert width!=0, 'width=0 check .bmp file' 
        
        self.wximg = self.scale_bitmap(wximg, 500/width)
        self.m_bitmap5.SetBitmap(self.wximg)
        self.m_mgr.Update()
        self.log(str(self.imi_path))
    def scale_bitmap(self, bitmap, scale):
        image = bitmap.ConvertToImage()
        width = image.GetWidth() * scale
        height = image.GetHeight() * scale
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.Bitmap(image, wx.BITMAP_TYPE_ANY)
        return result

    def read_pkl(self, event):
        assert self.hand_mode in [2,11], 'check hand_mode'
        if self.hand_mode == 11:
            dir_temp = os.path.join(self.img_folder, str(self.imi).zfill(10)+'.pkl')
        elif self.hand_mode == 2:
            dir_temp = os.path.join(self.img_folder, str(self.imi).zfill(10)+'_2p.pkl')
            # print('dir_temp =',dir_temp)
        dir_temp2 = os.path.join(self.img_folder, str(self.imi).zfill(10)+'.bmp')
        # print('dir_temp2=',dir_temp2)
        with open(dir_temp, 'rb') as f:
            data = pickle.load(f)
        self.point_temp = data['keypoint']
        self.covered_point = data['covered_point']
        # print('1')
        self.real_im = cv2.imread(dir_temp2)
        # print('2')
        self.reinit_tracker(event)
        # print('2.5')
        self.draw_bitmap()
        # print('3')
        self.log(dir_temp)
        # check hand_mode
        num = len(self.point_temp)
        # print('4')
        if num == 2: self.hand_mode = 2
        if num == 11: self.hand_mode = 11
        self.m_bitmap5.Bind(wx.EVT_MOUSE_EVENTS, self.getmousepos)
        # print('5')

    def Next(self, event):
        self.imi += 1
        try : 
            self.show_imi(self.imi)
            try:
                if self.checking_mode and not self.open_rm_bg_mode:
                    self.read_pkl(event)
            except :pass
        except : 
            self.imi -= 1
            wx.MessageBox('This is the last image of this folder', 'Cannot go next !',wx.OK )
    
    def Previous(self, event):
        self.imi -= 1
        try: 
            if self.open_rm_bg_mode:
                self.read_clean(event)
            else:
                self.show_imi(self.imi)
                self.read_pkl(event)
        except: 
            self.imi += 1
            wx.MessageBox('This is the first image of this folder', 'Cannot go previous !',wx.OK )
    def init_tracker(self, event):
        self.log('pick the keypoint to init tracker...')
        self.mytracks = [str(i) for i in range(self.hand_mode)]
        self.init_tracker_ = True
        # turn on get mouse
        self.m_bitmap5.Bind(wx.EVT_MOUSE_EVENTS, self.getmousepos)
        self.point_name = [str(i).zfill(2) for i in range(10)]
        self.point_temp = []
    def reinit_tracker(self,event):
        # print('in reinit')
        self.log('re-init tracker size')
        self.mytracks = [str(i) for i in range(self.hand_mode)]
        # print(1)
        for i,point in enumerate(self.point_temp):
            # print('for')
            self.mytracks[i] = MyTracker(self.real_im, point, self.tracking_roi_size)
        # print('out for')
        self.Redraw(event)
        # print('end reinit')

    def draw(self):
        # print('start def draw')
        ##### bad section ############# you need to solve #################
        try:
            int(self.real_im_width)
        except :
            self.real_im_width = 360
        #################################################################
     
        thres = 500/self.real_im_width
        rois, cens = [], []
        for i in range(len(self.point_temp)):
            ra, rb, rc, rd = self.mytracks[i].roi
            ca, cb = self.mytracks[i].center
            rois.append([ra*thres, rb*thres, rc*thres, rd*thres])
            cens.append([ca*thres, cb*thres])
            
        # print('1')
        # draw rect
        if self.roi_show_ :
            self.dc.SetPen(wx.Pen("red"))
            self.dc.SetBrush(wx.Brush("grey",style=wx.TRANSPARENT))
            for roi in rois:
                left, top, width, height = roi 
                pos = int(left), int(top)
                size = int(width), int(height)
                rect = wx.Rect(wx.Point(pos), wx.Size(size))
                self.dc.DrawRectangle(rect)
        # print('2')
        # draw links
        if self.link_show_:
            lines, pens = [], []
            for i,(start, end) in enumerate(self.links):
                try:
                    x1, y1 = cens[start]
                    x2, y2 = cens[end]
                    lines.append([x1, y1, x2, y2])
                    pens.append(wx.Pen(self.color_hand[int((i+1)%5)], 2))
                except :pass
            self.dc.DrawLineList(lines, pens)
        # print(3)
        # draw centers
        if self.keypoint_show_ :
            for i,cen in enumerate(cens):
                self.dc.SetPen(wx.Pen("black"))
                self.dc.SetBrush(wx.Brush(wx.Colour(0,255,0), wx.SOLID))
                size = self.keypoint_size
                
                if self.covered_point[i]:
                    self.dc.SetPen(wx.Pen("yellow"))
                    self.dc.SetBrush(wx.Brush(wx.Colour(255,255,0), wx.SOLID))
                    size = self.keypoint_size-1 if self.keypoint_size > 1 else 1
                self.dc.DrawCircle(cen,size)
        # print('out def draw')
    def draw_bitmap(self):
        # print('in')
        self.dc = wx.MemoryDC(self.wximg)
        # print('loaded')
        self.draw()
        # print('4.5')
        self.dc.SelectObject(wx.NullBitmap)
        # print('4')
        self.m_bitmap5.SetBitmap(self.wximg)
        # print('5')
        self.m_mgr.Update()
        # print('6')
    def manage_point(self, event):
    
        if len(self.point_temp) < self.hand_mode and len(self.point_temp) != -1 :
            self.point_temp.append(self.click)
            self.log('point(%d,%d) was added to be point[%d]'%(self.click[0],self.click[1],len(self.point_temp)-1))
            i = len(self.point_temp) - 1 # the last index
            self.mytracks[i] = MyTracker(self.real_im, self.click, self.tracking_roi_size)
            self.draw_bitmap()
        elif len(self.point_temp) == self.hand_mode:
            # manage point mode

            # check nearest point
            dist = np.array(self.point_temp)-np.array(self.click)
            nearest_index = np.argmin(dist[:,0]**2 + dist[:,1]**2)

            # check in_area
            dist = self.point_temp[nearest_index] - np.array(self.click)
            dist = dist[0]**2 + dist[1]**2

            # if in_area
            if dist < 1000:
                #move point
                self.move_point = True
                self.nearest_index = nearest_index

    def draw_move(self,event):
        #reset img
        self.imi_path = os.path.join(self.img_folder
                    , str(self.imi).zfill(10)+'.bmp')
        wximg = wx.Bitmap(self.imi_path, wx.BITMAP_TYPE_ANY)
        width = wximg.GetWidth()
        self.wximg = self.scale_bitmap(wximg, 500/width)

        
        self.dc = wx.MemoryDC(self.wximg)

        # re init nearest_point
        rm = self.point_temp[self.nearest_index]
        self.point_temp.insert(self.nearest_index,self.click)
        self.point_temp.remove(rm)
        self.mytracks[self.nearest_index] = MyTracker(self.real_im, self.click, self.tracking_roi_size)
        self.draw()
        self.dc.SelectObject(wx.NullBitmap)
        self.m_bitmap5.SetBitmap(self.wximg)

        self.m_mgr.Update()
    def set_covered_point(self):
        # check nearest point
        dist = np.array(self.point_temp)-np.array(self.click)
        nearest_index = np.argmin(dist[:,0]**2 + dist[:,1]**2)

        # check in_area
        dist = self.point_temp[nearest_index] - np.array(self.click)
        dist = dist[0]**2 + dist[1]**2

        # if in_area
        if dist < 100:
            # set to covered_point
            self.covered_point[nearest_index] = not self.covered_point[nearest_index]
            self.log('set coverd point of index_%d to %s'%(nearest_index,self.covered_point[nearest_index]))
                
    def Clear(self,event):
        self.show_imi(self.imi)
        self.point_temp = []
    def Redraw(self,event):
        #reset img
        self.imi_path = os.path.join(self.img_folder
                    , str(self.imi).zfill(10)+'.bmp')
        wximg = wx.Bitmap(self.imi_path, wx.BITMAP_TYPE_ANY)
        width = wximg.GetWidth()
        self.wximg = self.scale_bitmap(wximg, 500/width)
        #redraw
        self.draw_bitmap()
                
    def Back(self, event):
        #reset img
        self.imi_path = os.path.join(self.img_folder
                    , str(self.imi).zfill(10)+'.bmp')
        wximg = wx.Bitmap(self.imi_path, wx.BITMAP_TYPE_ANY)
        width = wximg.GetWidth()
        self.wximg = self.scale_bitmap(wximg, 500/width)

        #remove point
        self.point_temp.remove(self.point_temp[-1])
        self.draw_bitmap()
      
    def getmousepos(self, event):
        thres = self.real_im_width/500
        x, y = event.GetPosition()
        
        self.click = int(x*thres), int(y*thres)
        self.left_down = event.LeftDown()
        self.left_up = event.LeftUp()
        self.right_up = event.RightUp()
      
        if self.open_rm_bg_mode:
            if self.left_down and not self.set_mask_thres:
                self.color_picker.append(self.click)
                self.color_thres.append(10)
                self.set_mask_thres = True
            if self.set_mask_thres:
                last_point = self.color_picker[-1]
                dist = (last_point[0]-self.click[0])**2 + (last_point[1]-self.click[1])**2
                dist = dist**0.5/2
                self.color_thres[len(self.color_picker)-1] = dist
                self.show_imi(self.imi)
                self.show_mask(event)
            if self.left_up :
                self.set_mask_thres = False
            if self.right_up:
                # del a point
                dist = np.array(self.color_picker)-np.array(self.click)
                nearest_index = np.argmin(dist[:,0]**2 + dist[:,1]**2)
                # ck in_area
                dist = self.color_picker[nearest_index] - np.array(self.click)
                dist = dist[0]**2 + dist[1]**2
                if dist < 1000:
                    self.color_picker.remove(self.color_picker[nearest_index])
                    self.color_thres.remove(self.color_thres[nearest_index])
                else:
                    # clear all
                    self.color_picker = []
                    self.color_thres = []
                self.show_imi(self.imi)
                self.show_mask(event)
                
        else:
            if self.left_down:
                self.manage_point(event)
            if self.left_up:
                self.move_point = False
            if self.right_up:
                self.set_covered_point()
                self.Redraw(event)
            if self.move_point:
                self.draw_move(event)
                self.log('point[%d] is relocating to (%d, %d)'%(self.nearest_index,self.click[0],self.click[1]))
        
    def open_a_data( self, event ):
        with wx.FileDialog(self, "Open .bmp file", wildcard="bmp files (*.bmp)|*.bmp",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            
            try:
                #reset img
                wximg = wx.Bitmap(pathname, wx.BITMAP_TYPE_ANY)
                width = wximg.GetWidth()
                self.wximg = self.scale_bitmap(wximg, 500/width)
                assert self.hand_mode in [2,11]
                if self.hand_mode == 11:
                    dir_temp = pathname[:-4] + '.pkl'
                elif self.hand_mode == 2:
                    dir_temp = pathname[:-4] + '_2p.pkl'
                with open(dir_temp, "rb") as f:
                    data = pickle.load(f)
         
                self.point_temp = data['keypoint']
                self.covered_point = data['covered_point']
            
                self.img_folder = fileDialog.GetDirectory()
                # print(self.img_folder)
                fname = fileDialog.GetFilename()
                # print(fname)
                self.imi = int(fname[:-4])
                # print(self.imi)
                # print('bef read')
                self.read_pkl(event)
                # print('after read')
                self.log(pathname)
                self.checking_mode = True

            except :
                wx.MessageBox('Cannot open %s'%dir_temp,'Warning',wx.OK)
            
    def open_a_folder( self, event ):
        event.Skip()

    def goto_img(self,event):
        a = self.m_textCtrl3.GetValue()
        if a == 'go... .bmp':
            wx.MessageBox('please input a number of .bmp file.','Warning',wx.OK )
        else:
            try: 
                a = int(a)
                try:
                    self.show_imi(a)
                    self.imi = a
                    self.Clear(event)
                except :
                    wx.MessageBox('Cannot go to the file you want.\ncheck in the folder.','Cannot open .bmp',wx.OK )
            
            except:
                wx.MessageBox('This is not a number\nplease input a number of .bmp file.','Cannot go to ...',wx.OK )
            
    def key_on_go_bmp(self,event):
        key = event.GetKeyCode()
        if key==13: # enter
            self.goto_img(event)
    def click_on_go_bmp(self,event):
        self.m_textCtrl3.SetValue('')
        event.Skip()
    def roi_show(self,event):
        self.roi_show_ = True 
        self.m_menuItem17.Check(True)
        self.m_menuItem18.Check(False)
        self.Redraw(event)
    def roi_hide(self,event):
        self.roi_show_ = False 
        self.m_menuItem17.Check(False)
        self.m_menuItem18.Check(True)
        self.Redraw(event)
    def keypoint_show(self,event):
        self.keypoint_show_ = True
        self.m_menuItem171.Check(True)
        self.m_menuItem181.Check(False)
        self.Redraw(event)
    def keypoint_hide(self,event):
        self.keypoint_show_ = False
        self.m_menuItem171.Check(False)
        self.m_menuItem181.Check(True)
        self.Redraw(event)
    def link_show(self,event):
        self.link_show_ = True
        self.m_menuItem172.Check(True)
        self.m_menuItem182.Check(False)
        self.Redraw(event)
    def link_hide(self,event):
        self.link_show_ = False
        self.m_menuItem172.Check(False)
        self.m_menuItem182.Check(True)
        self.Redraw(event)
    def tracking_size_30( self, event ):
        self.tracking_roi_size = 30
        self.m_menuItem17311.Check(True)
        self.m_menuItem17312.Check(False)
        self.m_menuItem17313.Check(False)
        self.m_menuItem17314.Check(False)
        self.m_menuItem35.Check(False)
        self.reinit_tracker(event)
    def tracking_size_40( self, event ):
        self.tracking_roi_size = 40
        self.m_menuItem17311.Check(0)
        self.m_menuItem17312.Check(0)
        self.m_menuItem17313.Check(False)
        self.m_menuItem17314.Check(False)
        self.m_menuItem35.Check(False)
        self.reinit_tracker(event)
    def tracking_size_50( self, event ):
        self.tracking_roi_size = 50
        self.m_menuItem17311.Check(0)
        self.m_menuItem17312.Check(False)
        self.m_menuItem17313.Check(1)
        self.m_menuItem17314.Check(False)
        self.m_menuItem35.Check(False)
        self.reinit_tracker(event)
    def tracking_size_60( self, event ):
        self.tracking_roi_size = 60
        self.m_menuItem17311.Check(0)
        self.m_menuItem17312.Check(False)
        self.m_menuItem17313.Check(False)
        self.m_menuItem17314.Check(1)
        self.m_menuItem35.Check(False)
        self.reinit_tracker(event)
    def tracking_size_100( self, event ):
        self.tracking_roi_size = 100
        self.m_menuItem17311.Check(0)
        self.m_menuItem17312.Check(False)
        self.m_menuItem17313.Check(False)
        self.m_menuItem17314.Check(False)
        self.m_menuItem35.Check(1)
        self.reinit_tracker(event)
    def keypoint_size_mark(self,event):
        size = self.keypoint_size
        self.keysize1.Check(0)
        self.keysize2.Check(0)
        self.keysize3.Check(0)
        self.keysize5.Check(0)
        self.keysize10.Check(0)
        if size==1 : self.keysize1.Check(1)
        elif size==2 : self.keysize2.Check(1)
        elif size==3 : self.keysize3.Check(1)
        elif size==5 : self.keysize5.Check(1)
        elif size==10 : self.keysize10.Check(1)
        self.Redraw(event)
    def keypoint_size1(self, event):
        self.keypoint_size = 1
        self.keypoint_size_mark(event)
    def keypoint_size2(self, event):
        self.keypoint_size = 2
        self.keypoint_size_mark(event)
    def keypoint_size3(self, event):
        self.keypoint_size = 3
        self.keypoint_size_mark(event)
    def keypoint_size5(self, event):
        self.keypoint_size = 5
        self.keypoint_size_mark(event)
    def keypoint_size10(self, event):
        self.keypoint_size = 10
        self.keypoint_size_mark(event)
    def hand2(self,event):
        self.hand_mode = 2
        self.mode_hand2.Check(1)
        self.mode_hand11.Check(0)
        self.Clear(event)
    def hand11(self,event):
        self.hand_mode = 11
        self.mode_hand2.Check(0)
        self.mode_hand11.Check(1)
        self.Clear(event)
    def Delete(self, event):
        resp = wx.MessageBox('Do you want to delete this picture?', 'Confirm'
                                    ,wx.YES | wx.NO)
        if resp == wx.YES:
            #delete
            dir_temp = os.path.join(self.img_folder
                    , str(self.imi).zfill(10)+'.bmp')
            os.remove(dir_temp) # a bug
            self.log('deleted '+str(self.imi).zfill(10)+'.bmp')
            #rename
            i = 0
            while True:
                try:
                    scr = os.path.join(self.img_folder
                            , str(self.imi+1+i).zfill(10)+'.bmp')
                    dst = os.path.join(self.img_folder
                            , str(self.imi+i).zfill(10)+'.bmp')
                    os.rename(scr, dst)
                    i += 1
                except: break
        try:
            self.Clear(event)
        except:
            wx.MessageBox('This is the last image of this folder', 'Cannot go next !',wx.OK )
    

    def Save(self,event):

        if self.open_rm_bg_mode:
            name = 'clean_'+str(self.imi).zfill(10) + '.bmp'
            path = os.path.join(self.img_folder, name)
            self.show_imi(self.imi)
            filled_img = self.fill(self.real_im, self.color_picker, self.color_thres)
            cv2.imwrite(path,filled_img)
            self.Next(event)
            self.show_mask(event)
            self.log('saved '+name)
        else:
            if len(self.point_temp) == self.hand_mode:
                # output = [img_name, [11_points], [confirm]]
                img_name = str(self.imi).zfill(10)
                dictionary_data = {"keypoint": self.point_temp
                        , 'covered_point': self.covered_point}
                assert self.hand_mode in [2,11]
                if self.hand_mode == 11:
                    dir_temp = os.path.join(self.img_folder ,img_name + ".pkl")
                elif self.hand_mode == 2:
                    dir_temp = os.path.join(self.img_folder ,img_name + "_2p.pkl")
                with open(dir_temp, "wb") as f:
                    pickle.dump(dictionary_data, f)
                self.real_im = []
                self.point_temp = []
                self.Next(event)

                if self.off_tracker_mode:
                    self.point_temp = [] #clear points
                elif not self.checking_mode:
                    # update all trackers
                    for i in range(self.hand_mode):
                        if not self.covered_point[i]: # update if not be covered
                            self.mytracks[i].update(self.real_im)
                        p = self.mytracks[i].center
                        self.point_temp.append(p)
                    self.Redraw(event)
        

            else:
                wx.MessageBox('need %d keypoint to save'%self.hand_mode, 'Cannot save !',wx.OK )
        
    def on_key(self, event):
        key = event.GetKeyCode()
     
        if key == 32:
            if not self.stop_cam:
                if not self.vid_saving:
                    self.take_video(event)
                elif self.vid_saving:
                    self.stop_recording(event)
        event.Skip()
    def testmode(self, event):
        for i in range(20):
            self.Save(event)
 
    def test___(self,event):
        self.img_folder = 'video_temp/70'
        self.imi = 3
        self.stop_cam = True # stop showing camera
        
        self.show_imi(self.imi)
        
        self.init_tracker(event)
        self.point_temp = [(241, 531), (184, 348), (148, 239), (228, 318), (240, 175), (277, 315), (315, 159), (325, 329), (365, 192), (360, 442), (429, 339)]
        self.reinit_tracker(event)

        self.roi_show(event)
    def test_open_rm_bg(self, event):
        self.color_picker = []
        
        self.open_rm_bg_mode = True 
        self.checking_mode = False
        self.init_open_imgfolder = True
        fdir = 'video_temp\\07'
        self.img_folder = fdir
        self.imi = 1
        try:
            self.cap_.release()
        except :pass
        self.stop_cam = True # stop showing camera
        self.show_imi(self.imi)
        self.m_bitmap5.Bind(wx.EVT_MOUSE_EVENTS, self.getmousepos)
        
    def open_rm_bg(self, event):
        self.open_rm_bg_mode = True 
        self.checking_mode = False
        self.init_open_imgfolder = True
        fdir = ""  

        try:
            dir_temp = os.path.join(self.currentpath, 'video_temp')
            dlg = wx.DirDialog(self, defaultPath = dir_temp)
        except:        
            dlg = wx.DirDialog(self, defaultPath = self.currentpath)
        
        if dlg.ShowModal() == wx.ID_OK:
            fdir = dlg.GetPath()
            dlg.SetPath(fdir)
        dlg.Destroy()

        self.img_folder = fdir
        self.imi = 1
        try:
            self.cap_.release()
        except :pass
        self.stop_cam = True # stop showing camera
        self.show_imi(self.imi)
        self.m_bitmap5.Bind(wx.EVT_MOUSE_EVENTS, self.getmousepos)

    def show_mask(self, event):
        filled_img = self.fill(self.real_im, self.color_picker, self.color_thres)
        for x,y in self.color_picker:
            filled_img = cv2.circle(filled_img, (int(x),int(y)), 5, self.point_color, 2)
        if self.set_mask_thres:
            last_pick = self.color_picker[-1]
            filled_img = cv2.line(filled_img, last_pick, self.click, self.point_color, 1) 
        temp_name = 'wxbit_temp.bmp'
        cv2.imwrite(temp_name, filled_img)
        wximg = wx.Bitmap(temp_name, wx.BITMAP_TYPE_ANY)
        width = wximg.GetWidth()
        self.wximg = self.scale_bitmap(wximg, 500/width)
        self.m_bitmap5.SetBitmap(self.wximg)
        self.m_mgr.Update()
        self.log(str('masking img_%s'%str(self.imi).zfill(10)))

    def fill(self, frame, picker, thres):
        cs = []
        for i, (x, y) in enumerate(picker):
            blue,green,red = frame[y, x]
            val_red = frame[:,:,2]
            val_green = frame[:,:,1]
            val_blue = frame[:,:,0]
            thres = self.color_thres[i]
            c1 = (val_red>red-thres) * (val_red<red+thres)
            c2 = (val_green>green-thres) * (val_green<green+thres)
            c3 = (val_blue>blue-thres) * (val_blue<blue+thres)
            c = c1*c2*c3
            cs.append(c)
        for c in cs:

            frame[c] = self.bg_color
        return frame
    def bg_red(self,event):
        self.bg_color = (0,0,255)
        self.point_color = (255,0,0)
        self.show_imi(self.imi)
        self.show_mask(event)
    def bg_green(self,event):
        self.bg_color = (0,255,0)
        self.point_color = (0,0,255)
        self.show_imi(self.imi)
        self.show_mask(event)
    def bg_blue(self,event):
        self.bg_color = (255,0,0)
        self.point_color = (0,0,255)
        self.show_imi(self.imi)
        self.show_mask(event)
    def read_clean(self,event):
        temp_name = 'clean_'+str(self.imi).zfill(10)+'.bmp'
        path = os.path.join(self.img_folder, temp_name)
        wximg = wx.Bitmap(path, wx.BITMAP_TYPE_ANY)
        width = wximg.GetWidth()
        self.wximg = self.scale_bitmap(wximg, 500/width)
        self.m_bitmap5.SetBitmap(self.wximg)
        self.m_mgr.Update()
        self.log('loaded img_%s'%temp_name)
    def stop_track(self, event):
        self.off_tracker_mode = True

    
