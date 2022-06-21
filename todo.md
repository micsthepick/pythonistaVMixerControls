# todo

## ChannelView

### config
[X] config file
    [X] file based config
    [X] runtime config
    [X] optionally save config
    [ ] reconfigure on proxy error

### urgent fixes
[X] move slider control sensing region to same location as it got moved graphically (oops)

### base features
[X] channel name
    [X] get channel name
        [X] channel name
        [?] channel color
    [X] display channel name
        [X] text
        [?] coloring
[X] fader for volume on each channel
    [X] interactive faders
    [X] label for fader
    [X] link fader to socket
        [X] get value on load
        [X] set value when touch finished
[X] mute button on each channel
    [X] interactive button
    [X] pressing toggles on/off
[X] sends button for each channel
    [X] interactive send button
    [X] ui for sends
        [X] channels display
        [X] channels hooked up
[X] configuration modal
[X] disable DEBUG and print statments

### Graphics
[ ] fix orientation changes
    [X] stop rotation on phones

### Testing
[ ] regular ipad at home w/ proxy emulator
    [ ] 1 aux
        [ ] correct name
        [ ] Initial values > 0, =0, < 0, -inf
        [ ] set values shows up on page 3 fader
        [ ] sends
            [ ] correct amount
            [ ] correct name
            [ ] Initial values > 0, =0, < 0, -inf
            [ ] sends on faders works correctly
    [ ] 1 mtx
        [ ] correct name
        [ ] Initial values > 0, =0, < 0, -inf
        [ ] set values shows up on page 3 fader
        [ ] sends
            [ ] correct amount
            [ ] correct name
            [ ] Initial values > 0, =0, < 0, -inf
            [ ] sends on faders works correctly
    [ ] mains
        [ ] correct name
        [ ] Initial values > 0, =0, < 0, -inf
        [ ] set values shows up on main fader
        [ ] sends
            [ ] correct amount
            [ ] correct name
            [ ] Initial values > 0, =0, < 0, -inf
            [ ] main faders works correctly
[ ] ipad mini at home w/ proxy emulator
    [ ] no layout issues
        [ ] test at least one fader and send fader
[ ] phone at home w/ proxy emulator
    [ ] no layout issues
        [ ] test at least one fader and send fader
[ ] ipad at church
[ ] ipad mini at church
    [ ] no layout issues
        [ ] test at least one fader and send fader
[ ] phone at church
    [ ] no layout issues
        [ ] test at least one fader and send fader

### optional extras
[X] scroll by dragging
[ ] panning (L,R,C)?
[ ] MAC
[X] layout improvments for small devices





## effectsView

### ?
[ ] decide whether to make this a seperate thing to ChannelView, or to not implement

### features
[ ] channel ops
    [ ] parametric eq
        [ ] toggle button
    [ ] hpf
        [ ] toggle button
    [ ] gate / comp
        [ ] toggle button
    


