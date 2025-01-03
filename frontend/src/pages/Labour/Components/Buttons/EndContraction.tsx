import { Button } from '@mantine/core';
import { useAuth } from 'react-oidc-context';
import { EndContractionRequest, LabourResponse } from '../../../../client';
import { StopwatchHandle } from '../Stopwatch/Stopwatch';
import { RefObject } from 'react';

export default function EndContractionButton(
    {intensity, setLabour, stopwatchRef}: {intensity: number, setLabour: Function, stopwatchRef: RefObject<StopwatchHandle>}
) {
    const auth = useAuth()
    const endContraction = async () => {
        stopwatchRef.current?.stop()
        stopwatchRef.current?.reset()
        try {
            const headers = {
                'Authorization': `Bearer ${auth.user?.access_token}`,
                'Content-Type': 'application/json'
            }
            const requestBody: EndContractionRequest = {
                "end_time": new Date().toISOString(),
                "intensity": intensity,
                "notes": null
            }
            const response = await fetch(
                'http://localhost:8000/api/v1/labour/contraction/end',
                { method: 'PUT', headers: headers, body: JSON.stringify(requestBody) }
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data: LabourResponse = await response.json();
            setLabour(data.labour)
        } catch (err) {
            console.error('Error starting contraction:', err);
        }
    }
    return <Button radius="lg" size='xl' variant="white" onClick={endContraction}>End Contraction</Button>;
}