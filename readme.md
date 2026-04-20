# Pod Tooling

Shell scripts for podcast production and content marketing workflows.

## Capabilities

- **Frame rate sync** — synchronizes audio/video frame rates across clips

## Structure

```
bash/
  __index.sh      # entry point — source this to load all utils
blanc-beats/      # beat/audio related scripts
blanc-clips/      # video clip scripts
```

## Setup

Source the index file in your shell config:

```sh
echo "\nsource '$HOME/Documents/GitHub/pod-tooling/bash/__index.sh'" >> ~/.zshrc
```
