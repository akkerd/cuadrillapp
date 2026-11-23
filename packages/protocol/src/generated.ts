// Generado por make gen desde apps/server. No editar a mano.

export interface CuadrillappProtocol {}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "AdminSet".
 */
export interface AdminSet {
  isAdmin: boolean;
  participantId: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryAdd".
 */
export interface CategoryAdd {
  emoji: string;
  name: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryDelete".
 */
export interface CategoryDelete {
  categoryId: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryMove".
 */
export interface CategoryMove {
  categoryId: string;
  direction: -1 | 1;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryResultView".
 */
export interface CategoryResultView {
  categoryId: string;
  emoji: string;
  entries: RankEntryView[];
  name: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RankEntryView".
 */
export interface RankEntryView {
  candidateId: string;
  count: number;
  emoji: string;
  name: string;
  position: number | null;
  score: number | null;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryUpdate".
 */
export interface CategoryUpdate {
  categoryId: string;
  emoji: string;
  name: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "CategoryView".
 */
export interface CategoryView {
  emoji: string;
  id: string;
  name: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "JoinResult".
 */
export interface JoinResult {
  code: string;
  participantId: string;
  token: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "KickedEvent".
 */
export interface KickedEvent {
  code: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ManualAdd".
 */
export interface ManualAdd {
  emoji: string;
  name: string;
  role?: "candidate" | "voter";
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "Me".
 */
export interface Me {
  isAdmin: boolean;
  participantId: string;
  progress: Progress;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "Progress".
 */
export interface Progress {
  given: number;
  total: number;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ParticipantKick".
 */
export interface ParticipantKick {
  participantId: string;
}
/**
 * Cambia mi perfil o, si soy admin, el rol de otro o el perfil de un manual.
 *
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ParticipantUpdate".
 */
export interface ParticipantUpdate {
  emoji?: string | null;
  name?: string | null;
  participantId?: string | null;
  role?: ("candidate" | "voter") | null;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ParticipantView".
 */
export interface ParticipantView {
  connected: boolean;
  done: boolean;
  emoji: string;
  id: string;
  isAdmin: boolean;
  isManual: boolean;
  name: string;
  progress: Progress | null;
  role: "candidate" | "voter";
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "PeekResult".
 */
export interface PeekResult {
  code: string;
  full: boolean;
  phase: "lobby" | "voting" | "results";
  title: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RejoinResult".
 */
export interface RejoinResult {
  participantId: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ReplacedEvent".
 */
export interface ReplacedEvent {
  code: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ResultsView".
 */
export interface ResultsView {
  byCategory: CategoryResultView[];
  overall: RankEntryView[];
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomCreate".
 */
export interface RoomCreate {
  emoji: string;
  name: string;
  role?: "candidate" | "voter";
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomJoin".
 */
export interface RoomJoin {
  code: string;
  emoji: string;
  name: string;
  role?: "candidate" | "voter";
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomLeave".
 */
export interface RoomLeave {}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomPeek".
 */
export interface RoomPeek {
  code: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomRejoin".
 */
export interface RoomRejoin {
  code: string;
  token: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoomSnapshot".
 */
export interface RoomSnapshot {
  categories: CategoryView[];
  code: string;
  me: Me;
  myScores: ScoreView[];
  participants: ParticipantView[];
  phase: "lobby" | "voting" | "results";
  proxyScores: ScoreView[];
  results: ResultsView | null;
  startCheck: StartCheck;
  title: string;
  version: number;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ScoreView".
 */
export interface ScoreView {
  candidateId: string;
  categoryId: string;
  quarters: number;
  voterId: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "StartCheck".
 */
export interface StartCheck {
  missing: ("categories" | "candidates" | "participants")[];
  ready: boolean;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "RoundNew".
 */
export interface RoundNew {}
/**
 * Fija (o borra con `quarters: null`) una nota en cuartos de punto.
 *
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "ScoreSet".
 */
export interface ScoreSet {
  asParticipantId?: string | null;
  candidateId: string;
  categoryId: string;
  quarters: number | null;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "TitleSet".
 */
export interface TitleSet {
  title: string;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "VoterDone".
 */
export interface VoterDone {
  asParticipantId?: string | null;
  done: boolean;
}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "VotingReopen".
 */
export interface VotingReopen {}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "VotingReveal".
 */
export interface VotingReveal {}
/**
 * This interface was referenced by `CuadrillappProtocol`'s JSON-Schema
 * via the `definition` "VotingStart".
 */
export interface VotingStart {}
