# todo

## ChannelView

### config
[X] config file
    [X] file based config
    [X] runtime config
    [X] optionally save config
    [X] reconfigure on proxy error

### urgent fixes
[X] move slider control sensing region to same location as it got moved graphically (oops)

### base features
[X] channel name
    [X] get channel name
        [X] channel name
    [X] display channel name
        [X] text
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
[ ] conditionally show mute for mains sends (inputs)

### Graphics
[ ] fix orientation changes
    [X] stop rotation on phones
    [ ] allow for shuffling of elements vertically when rotating
[X] visual feeback
    [X] suceeded commands
    [X] failed commands
[X] change server settings
[X] hide mute for mains

[ ] channel rename view

[ ] top bar
    [X] refresh button
    [X] configure proxy button
    [ ] show ip address?
    
### Refresh functionality
[ ] Refresh button
    [X] Update (appropriate) sliders on refresh
    [X] change mute / unmute to same button
    [X] update state of mute / unmute on refresh
    [ ] fix layout issues
    [ ] refresh linked channels automatically
    
### persistent connection
[ ] stub connection on class

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
[ ] grouping
[ ] MAC - mains C
[ ] pre-amp ajdust
[X] layout improvments for small devices
[ ] channel display filtering
    [ ] select channels
    [ ] only show acl enabled features





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
    


