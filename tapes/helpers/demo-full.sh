#!/bin/bash
# Full simulated Claude Code session — redact PII from a PDF
# Renders the entire UI frame by frame with realistic delays

# Colors matching Claude Code's TUI
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'
RESET='\033[0m'
WHITE='\033[97m'
GRAY='\033[90m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
MAGENTA='\033[35m'
BLUE='\033[34m'
BG_DARK='\033[48;5;236m'
ORANGE='\033[38;5;208m'

clear

# ── Claude Code header ──
echo -e "${BOLD}${ORANGE}╭────────────────────────────────────────────────────────────────────╮${RESET}"
echo -e "${BOLD}${ORANGE}│${RESET}  ${BOLD}${WHITE}◆ Claude Code${RESET}  ${DIM}v1.0.26${RESET}                                          ${BOLD}${ORANGE}│${RESET}"
echo -e "${BOLD}${ORANGE}╰────────────────────────────────────────────────────────────────────╯${RESET}"
echo
echo -e "  ${DIM}cwd: ~/projects/patient-data${RESET}"
echo
sleep 0.8

# ── User prompt ──
echo -e "${BOLD}${BLUE}❯${RESET} ${WHITE}Redact all SSNs and email addresses from patient-records.pdf${RESET}"
echo
sleep 1.2

# ── Thinking indicator ──
echo -ne "  ${DIM}${MAGENTA}⟡ Thinking…${RESET}"
sleep 1.5
echo -e "\r  ${DIM}${MAGENTA}⟡ Thinking… done${RESET}                    "
echo

# ── Skill activation ──
echo -e "  ${DIM}Using skill: ${CYAN}nutrient-document-processing${RESET}"
echo
sleep 0.6

# ── Tool call ──
echo -e "  ${YELLOW}⬡ Tool: nutrient_redact${RESET}"
echo -e "  ${DIM}┌──────────────────────────────────────────────────────────────┐${RESET}"
echo -e "  ${DIM}│${RESET}  input:    ${WHITE}patient-records.pdf${RESET}                                ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  output:   ${WHITE}patient-records-redacted.pdf${RESET}                        ${DIM}│${RESET}"
echo -e "  ${DIM}│${RESET}  patterns: ${CYAN}[social-security-number, email-address]${RESET}              ${DIM}│${RESET}"
echo -e "  ${DIM}└──────────────────────────────────────────────────────────────┘${RESET}"
echo
sleep 0.8

# ── Processing animation ──
for i in 1 2 3; do
    echo -ne "\r  ${YELLOW}⏳ Calling Nutrient DWS API"
    for j in $(seq 1 $i); do echo -ne "."; done
    echo -ne "${RESET}      "
    sleep 0.5
done
echo -e "\r  ${GREEN}✓${RESET} ${WHITE}API call complete${RESET} ${DIM}(1.2s, 2 credits used)${RESET}          "
echo
sleep 0.5

# ── Results ──
echo -e "  ${GREEN}${BOLD}Redaction complete:${RESET}"
echo -e "    ${WHITE}•${RESET} ${BOLD}4${RESET} Social Security Numbers redacted"
echo -e "    ${WHITE}•${RESET} ${BOLD}7${RESET} email addresses redacted"
echo -e "    ${WHITE}•${RESET} ${BOLD}11${RESET} total redaction annotations applied"
echo
sleep 0.5

echo -e "  ${GREEN}📄 Created:${RESET} ${BOLD}${WHITE}patient-records-redacted.pdf${RESET} ${DIM}(248 KB)${RESET}"
echo
echo -e "  ${DIM}All matched patterns have been permanently removed from the document.${RESET}"
echo -e "  ${DIM}The redacted areas are filled with black boxes and the underlying${RESET}"
echo -e "  ${DIM}text has been irreversibly deleted.${RESET}"
echo

# Hold the final frame
sleep 5
