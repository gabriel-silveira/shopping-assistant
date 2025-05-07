/**
 * Substitui texto delimitado por asteriscos duplos (ex: **texto**)
 * por tags HTML <b> (ex: <b>texto</b>).
 *
 * @param text A string de entrada que pode conter texto para ser formatado em negrito.
 * @returns A string com as substituições feitas.
 */
export function boldenDoubleAsterisks(text: string): string {
  // Expressão Regular:
  // \*\*     : Corresponde aos dois asteriscos de abertura (escapados, pois * é um metacaractere).
  // (      : Inicia um grupo de captura.
  //   .+?  : Corresponde a qualquer caractere (.), uma ou mais vezes (+), de forma não gulosa (?).
  //          "Não gulosa" (lazy) é importante para que ele pare no primeiro par de asteriscos de fechamento,
  //          em vez de continuar até o último par em uma linha com múltiplas ocorrências.
  // )      : Fecha o grupo de captura. O conteúdo capturado estará disponível como $1 na substituição.
  // \*\*     : Corresponde aos dois asteriscos de fechamento (escapados).
  // g        : Flag global, para substituir todas as ocorrências na string, não apenas a primeira.
  const regex = /\*\*(.+?)\*\*/g;

  // A string de substituição:
  // <b>$1</b> : Onde $1 é o conteúdo capturado pelo primeiro grupo na regex (o texto entre os asteriscos).
  const replacement = '<b>$1</b>';

  return text.replace(regex, replacement);
}
