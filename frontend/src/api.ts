import axios from 'axios'

interface AgentResponse {
    triage?: {
        emergency: string;
        severity: number;
    };
    instructions?: {
        summary: string;
        steps: string[] | string;
    };
    error?: string;
    details?: string;
}

export type ChatRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
    role: ChatRole
    content: string
}

export interface ContinueResponse {
    ok: boolean
    messages: ChatMessage[]
    result: any
}
