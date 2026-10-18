#!/bin/bash
# mixvoice.sh <out.wav> [id=file ...]: lays voice/lines_v2/<id>.mp3 at voice/timing_v2.tsv (run in pitch/intro); overrides map an id to another file
OUT=$1; shift; declare -A OV; for kv in "$@"; do OV[${kv%%=*}]=${kv#*=}; done
IN=""; F=""; i=0; L=""
while IFS=$'\t' read -r id st tp; do [ "$id" = line ] && continue; i=$((i+1)); f=${OV[$id]:-voice/lines_v2/$id.mp3}; IN="$IN -i $f"
  ms=$(awk "BEGIN{printf \"%d\", $st*1000}")
  F="$F[$((i-1)):a]aresample=48000,aformat=channel_layouts=mono,atempo=$tp,adelay=$ms:all=1[a$i];"; L="$L[a$i]"; done < voice/timing_v2.tsv
F="$F${L}amix=inputs=$i:normalize=0:dropout_transition=0,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000,apad=whole_dur=59.086875,atrim=0:59.086875,aformat=channel_layouts=stereo[aout]"
ffmpeg -v error -y $IN -filter_complex "$F" -map "[aout]" -c:a pcm_s16le "$OUT"
