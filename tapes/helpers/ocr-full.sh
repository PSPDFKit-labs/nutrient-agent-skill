#!/bin/bash
# Full simulated Claude Code session — OCR + text extraction

BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'
WHITE='\033[97m'
GRAY='\033[90m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
MAGENTA='\033[35m'
BLUE='\033[34m'
ORANGE='\033[38;5;208m'

clear

# ── Claude Code header ──
echo -e "${BOLD}${ORANGE}╭────────────────────────────────────────────────────────────────────╮${RESET}"
echo -e "${BOLD}${ORANGE}│${RESET}  ${BOLD}${WHITE}◆ Claude Code${RESET}  ${DIM}v1.0.26${RESET}                                          ${BOLD}${ORANGE}│${RESET}"
echo -e "${BOLD}${ORANGE}╰────────────────────────────────────────────────────────────────────╯${RESET}"
echo
echo -e "  ${DIM}cwd: ~/projects/legal-docs${RESET}"
echo
sleep 0.8

# ── User prompt ──
echo -e "${BOLD}${BLUE}❯${RESET} ${WHITE}OCR scanned-contract.pdf in English and extract the text to contract.txt${RESET}"
echo
sleep 1.2

# ── Thinking ──
echo -ne "  ${DIM}${MAGENTA}⟡ Thinking…${RESET}"
sleep 1.2
echo -e "\r  ${DIM}${MAGENTA}⟡ Thinking… done${RESET}                    "
echo

echo -e "  ${DIM}Using skill: ${CYAN}nutrient-document-processing${RESET}"
echo
sleep 0.5

# ── Step 1: OCR ──
echo -e "  ${YELLOW}⬡ Step 1: nutrient_ocr${RESET}"
echo -e "  ${DIM}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "  ${DIM}│${RESET}  input:    ${WHITE}scanned-contract.pdf${RESET}                               ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  output:   ${WHITE}scanned-contract-ocr.pdf${RESET}                           ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  language: ${CYAN}english${RESET}                                             ${DIM}│${RESET}"
echo -e "  ${DIM}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
sleep 0.6

for i in 1 2 3; do
    echo -ne "\r  ${YELLOW}⏳ Running OCR"
    for j in $(seq 1 $i); do echo -ne "."; done
    echo -ne "${RESET}      "
    sleep 0.5
done
echo -e "\r  ${GREEN}✓${RESET} ${WHITE}OCR complete${RESET} ${DIM}(2.8s, 4 credits used)${RESET}              "
echo
sleep 0.4

# ── Step 2: Extract ──
echo -e "  ${YELLOW}⬡ Step 2: nutrient_extract_text${RESET}"
echo -e "  ${DIM}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "  ${DIM}│${RESET}  input:    ${WHITE}scanned-contract-ocr.pdf${RESET}                           ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  mode:     ${CYAN}text${RESET}                                                ${DIM}│${RESET}"
echo -e "  ${DIM}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
sleep 0.5

echo -ne "  ${YELLOW}⏳ Extracting text...${RESET}"
sleep 1
echo -e "\r  ${GREEN}✓${RESET} ${WHITE}Text extracted${RESET} ${DIM}(0.4s, 1 credit used)${RESET}            "
echo
sleep 0.4

# ── Results ──
echo -e "  ${GREEN}${BOLD}Done:${RESET}"
echo -e "    ${WHITE}•${RESET} OCR applied — 12 pages processed, 98.4% confidence"
echo -e "    ${WHITE}•${RESET} Text extracted — 4,231 words"
echo -e "    ${WHITE}•${RESET} Saved to ${BOLD}contract.txt${RESET}"
echo
echo -e "  ${GREEN}📄 Created:${RESET} ${BOLD}${WHITE}scanned-contract-ocr.pdf${RESET} ${DIM}(searchable PDF, 1.2 MB)${RESET}"
echo -e "  ${GREEN}📝 Created:${RESET} ${BOLD}${WHITE}contract.txt${RESET} ${DIM}(plain text, 28 KB)${RESET}"
echo

sleep 3
