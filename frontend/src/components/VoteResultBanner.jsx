export default function VoteResultBanner({ result }) {
  if (!result) return null;

  const { passed, yes, no } = result;

return (
    <div
        style={{
            position: 'fixed',
            top: '40%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: passed ? 'green' : 'darkred',
            color: 'white',
            padding: '2rem 3rem',
            borderRadius: '1rem',
            fontSize: '1.5rem',
            boxShadow: '0 0 20px rgba(0,0,0,0.6)',
            zIndex: 9999,
            textAlign: 'center',
        }}
    >
        <div>
            {passed ? '✅ Gobierno aprobado' : '❌ Gobierno rechazado'}
        </div>
        <div>
            -{yes} a favor, {no} en contra-
        </div>
    </div>
);
}
