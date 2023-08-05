package belligerents;

import java.awt.image.BufferedImage;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import belligerents.weapon.Weapon;
import builders.AttackerDataModel;
import game.Game;

public class NormalAttacker extends Attacker {
	private static final Logger LOGGER = LogManager.getLogger(NormalAttacker.class);

	public NormalAttacker(AttackerDataModel attackerDataModel, Game game, int x, int y) {

		super(attackerDataModel, game, x, y);
		LOGGER.info("Create NormalAttacker at x:" + x + ", y:" + y);
	}

	@Override
	public void notify_movement() {
//		for (GameObjectListerner allyBoatListener : movement_listeners) {
//			allyBoatListener.on_normal_attacker_moved(this);
//		}
	}

	@Override
	protected void right_border_of_game_board_reached() {
		setX_speed(getX_speed() * -1);
	}

	@Override
	protected void left_border_of_game_board_reached() {
	}

	@Override
	public void impact_now(Weapon weapon) {
		super.impact_now(weapon);
	}

	@Override
	protected BufferedImage get_graphical_representation_as_buffered_image() {
		return getNormal_attacker_buffered_image(this);
	}

	@Override
	protected void down_border_of_game_board_reached() {
		// TODO Auto-generated method stub

	}

}