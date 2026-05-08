parser grammar Fortios_vdom;

options {
  tokenVocab = FortiosLexer;
}

c_vdom: VDOM newline cv_edit*;

cv_edit: EDIT vdom_name newline cve* NEXT newline;

// Up to 31 characters
vdom_name: str;

cve: CONFIG (
    c_system
    | c_firewall
    | c_router
    | IGNORED_CONFIG_BLOCK
) END NEWLINE
;
