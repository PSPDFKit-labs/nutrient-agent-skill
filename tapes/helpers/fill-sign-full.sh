#!/bin/bash
# Full simulated Claude Code session — fill form + digital signature

BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'
WHITE='\033[97m'
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
echo -e "  ${DIM}cwd: ~/projects/hr-onboarding${RESET}"
echo
sleep 0.8

# ── User prompt ──
echo -e "${BOLD}${BLUE}❯${RESET} ${WHITE}Fill employee-onboarding.pdf with name 'Jane Smith', start date${RESET}"
echo -e "  ${WHITE}'2026-03-01', department 'Engineering', then sign it${RESET}"
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

# ── Step 1: Fill form ──
echo -e "  ${YELLOW}⬡ Step 1: nutrient_fill_form${RESET}"
echo -e "  ${DIM}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "  ${DIM}│${RESET}  input:  ${WHITE}employee-onboarding.pdf${RESET}                                ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  fields:                                                      ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}    ${CYAN}employee_name${RESET}:  ${WHITE}\"Jane Smith\"${RESET}                              ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}    ${CYAN}start_date${RESET}:     ${WHITE}\"2026-03-01\"${RESET}                             ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}    ${CYAN}department${RESET}:     ${WHITE}\"Engineering\"${RESET}                            ${DIM}│${RESET}"
echo -e "  ${DIM}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
sleep 0.6

echo -ne "  ${YELLOW}⏳ Filling form fields...${RESET}"
sleep 1
echo -e "\r  ${GREEN}✓${RESET} ${WHITE}Form filled${RESET} ${DIM}(0.8s, 1 credit used)${RESET}               "
echo
sleep 0.4

# ── Step 2: Sign ──
echo -e "  ${YELLOW}⬡ Step 2: nutrient_sign${RESET}"
echo -e "  ${DIM}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "  ${DIM}│${RESET}  input:         ${WHITE}employee-onboarding-filled.pdf${RESET}                  ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  output:        ${WHITE}employee-onboarding-signed.pdf${RESET}                  ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  signatureType: ${CYAN}cms${RESET}                                             ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  signerName:    ${WHITE}\"Jane Smith\"${RESET}                                   ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  reason:        ${WHITE}\"Employee onboarding\"${RESET}                          ${DIM}│${RESET}"
echo -e "  ${DIM}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
sleep 0.6

echo -ne "  ${YELLOW}⏳ Applying digital signature...${RESET}"
sleep 1.2
echo -e "\r  ${GREEN}✓${RESET} ${WHITE}Document signed${RESET} ${DIM}(1.1s, 1 credit used)${RESET}          "
echo
sleep 0.4

# ── Results ──
echo -e "  ${GREEN}${BOLD}Done:${RESET}"
echo -e "    ${WHITE}•${RESET} 3 form fields filled"
echo -e "    ${WHITE}•${RESET} CMS digital signature applied"
echo -e "    ${WHITE}•${RESET} Total: 2 credits used"
echo
echo -e "  ${GREEN}📄 Created:${RESET} ${BOLD}${WHITE}employee-onboarding-signed.pdf${RESET} ${DIM}(342 KB)${RESET}"
echo

sleep 3
