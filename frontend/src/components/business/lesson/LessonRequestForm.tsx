import { Button } from '../../Button';
import { Card, CardContent } from '../../Card';
import { Field } from '../../Field';

export function LessonRequestForm({
  studentId,
  vocabInput,
  onStudentIdChange,
  onVocabInputChange,
  onSubmit,
  loading,
}: {
  studentId: string;
  vocabInput: string;
  onStudentIdChange: (value: string) => void;
  onVocabInputChange: (value: string) => void;
  onSubmit: () => void;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardContent className="ui-form-grid">
        <Field label="Student ID" value={studentId} onChange={(e) => onStudentIdChange(e.target.value)} />
        <Field
          label="Vocabulary"
          value={vocabInput}
          onChange={(e) => onVocabInputChange(e.target.value)}
          placeholder="apple,milk,hungry"
          hint="Comma-separated words for the next lesson."
        />
        <div className="ui-form-grid__actions">
          <Button variant="primary" onClick={onSubmit} disabled={loading}>
            {loading ? 'Generating...' : 'Generate next lesson'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
