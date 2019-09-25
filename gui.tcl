#############################################################################
# Generated by PAGE version 4.25.1
#  in conjunction with Tcl version 8.6
#  Sep 25, 2019 08:35:57 AM +07  platform: Windows NT
set vTcl(timestamp) ""


if {!$vTcl(borrow) && !$vTcl(template)} {

set vTcl(actual_gui_bg) #d9d9d9
set vTcl(actual_gui_fg) #000000
set vTcl(actual_gui_analog) #ececec
set vTcl(actual_gui_menu_analog) #ececec
set vTcl(actual_gui_menu_bg) #d9d9d9
set vTcl(actual_gui_menu_fg) #000000
set vTcl(complement_color) #d9d9d9
set vTcl(analog_color_p) #d9d9d9
set vTcl(analog_color_m) #ececec
set vTcl(active_fg) #000000
set vTcl(actual_gui_menu_active_bg)  #ececec
set vTcl(active_menu_fg) #000000
}




proc vTclWindow.top42 {base} {
    global vTcl
    if {$base == ""} {
        set base .top42
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl::widgets::core::toplevel::createCmd $top -class Toplevel \
        -menu "$top.m43" -background $vTcl(actual_gui_bg) \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 1024x680+623+25
    update
    # set in toplevel.wgt.
    global vTcl
    global img_list
    set vTcl(save,dflt,origin) 0
    wm maxsize $top 1370 729
    wm minsize $top 120 1
    wm overrideredirect $top 0
    wm resizable $top 0 0
    wm deiconify $top
    wm title $top "New Toplevel"
    vTcl:DefineAlias "$top" "top_level" vTcl:Toplevel:WidgetProc "" 1
    set site_3_0 $top.m43
    menu $site_3_0 \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(pr,menubgcolor) -font TkMenuFont \
        -foreground $vTcl(pr,menufgcolor) -tearoff 0 
    $site_3_0 add cascade \
        -menu "$site_3_0.men44" -activebackground $vTcl(analog_color_m) \
        -activeforeground #000000 -background $vTcl(pr,menubgcolor) \
        -font TkMenuFont -foreground $vTcl(pr,menufgcolor) -label File 
    menu $site_3_0.men44 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(pr,menubgcolor) -font {-family {Segoe UI} -size 9} \
        -foreground black -tearoff 0 
    $site_3_0.men44 add command \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(pr,menubgcolor) -command load_file -font TkMenuFont \
        -foreground $vTcl(pr,menufgcolor) -label Load 
    $site_3_0.men44 add separator \
        -background $vTcl(pr,menubgcolor) 
    $site_3_0.men44 add command \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(pr,menubgcolor) -command settings -font TkMenuFont \
        -foreground $vTcl(pr,menufgcolor) -label Settings 
    $site_3_0.men44 add command \
        -activebackground $vTcl(analog_color_m) -activeforeground #000000 \
        -background $vTcl(pr,menubgcolor) -command exit -font TkMenuFont \
        -foreground $vTcl(pr,menufgcolor) -label Exit 
    frame $top.fra45 \
        -borderwidth 2 -relief groove -background $vTcl(actual_gui_bg) \
        -height 655 -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black -width 705 
    vTcl:DefineAlias "$top.fra45" "canvas_frame" vTcl:WidgetProc "top_level" 1
    set site_3_0 $top.fra45
    canvas $site_3_0.can48 \
        -background $vTcl(actual_gui_bg) -closeenough 1.0 -height 655 \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -insertbackground black -relief ridge -selectbackground #c4c4c4 \
        -selectforeground black -takefocus 0 -width 705 
    vTcl:DefineAlias "$site_3_0.can48" "canvas" vTcl:WidgetProc "top_level" 1
    place $site_3_0.can48 \
        -in $site_3_0 -x 0 -y 0 -width 705 -relwidth 0 -height 655 \
        -relheight 0 -anchor nw -bordermode ignore 
    labelframe $top.lab50 \
        -font TkDefaultFont -foreground black -text Data \
        -background $vTcl(actual_gui_bg) -height 665 \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -width 280 
    vTcl:DefineAlias "$top.lab50" "data_frame" vTcl:WidgetProc "top_level" 1
    frame $top.fra51 \
        -borderwidth 2 -relief groove -background $vTcl(actual_gui_bg) \
        -height 25 -highlightbackground $vTcl(actual_gui_bg) \
        -highlightcolor black -width 1025 
    vTcl:DefineAlias "$top.fra51" "Frame1" vTcl:WidgetProc "top_level" 1
    set site_3_0 $top.fra51
    label $site_3_0.lab66 \
        -activebackground #f9f9f9 -activeforeground black \
        -background $vTcl(actual_gui_bg) -disabledforeground #a3a3a3 \
        -font TkDefaultFont -foreground black \
        -highlightbackground $vTcl(actual_gui_bg) -highlightcolor black \
        -text {x: } 
    place $site_3_0.lab66 \
        -in $site_3_0 -x 10 -y 0 -width 34 -relwidth 0 -height 11 \
        -relheight 0 -anchor nw -bordermode ignore 
    ###################
    # SETTING GEOMETRY
    ###################
    place $top.fra45 \
        -in $top -x 10 -y 10 -width 705 -relwidth 0 -height 655 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.lab50 \
        -in $top -x 730 -y 0 -width 280 -relwidth 0 -height 665 -relheight 0 \
        -anchor nw -bordermode ignore 
    place $top.fra51 \
        -in $top -x 0 -y 680 -width 1025 -relwidth 0 -height 25 -relheight 0 \
        -anchor nw -bordermode ignore 

    vTcl:FireEvent $base <<Ready>>
}

set btop ""
if {$vTcl(borrow)} {
    set btop .bor[expr int([expr rand() * 100])]
    while {[lsearch $btop $vTcl(tops)] != -1} {
        set btop .bor[expr int([expr rand() * 100])]
    }
}
set vTcl(btop) $btop
Window show .
Window show .top42 $btop
if {$vTcl(borrow)} {
    $btop configure -background plum
}

